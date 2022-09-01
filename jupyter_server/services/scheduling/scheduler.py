from abc import ABC, abstractmethod
from multiprocessing import Process
from typing import List

import psutil
from jupyter_core.paths import jupyter_data_dir
from jupyter_scheduling.config import ExecutionConfig
from jupyter_scheduling.models import (
    CountJobsQuery,
    CreateJob,
    CreateJobDefinition,
    DescribeJob,
    DescribeJobDefinition,
    ListJobDefinitionsQuery,
    ListJobsQuery,
    ListJobsResponse,
    SortDirection,
    Status,
    UpdateJob,
)
from jupyter_scheduling.orm import Job, create_session
from jupyter_scheduling.utils import create_output_filename, timestamp_to_int
from sqlalchemy import and_, asc, desc, func


class BaseScheduler(ABC):
    """Base class for schedulers. A default implementation
    is provided in the `Scheduler` class, but extension creators
    can provide their own scheduler by subclassing this class.
    By implementing this class, you will replace both the service
    API and the persistence layer for the scheduler.
    """

    @abstractmethod
    def create_job(self, model: CreateJob) -> str:
        """Creates a new job record, may trigger execution of the job.
        In case a task runner is actually handling execution of the jobs,
        this method should just create the job record.
        """
        pass

    @abstractmethod
    def update_job(self, model: UpdateJob):
        """Updates job metadata in the persistence store,
        for example name, status etc. In case of status
        change to STOPPED, should call stop_job
        """
        pass

    @abstractmethod
    def list_jobs(self, query: ListJobsQuery) -> ListJobsResponse:
        """Returns list of all jobs filtered by query"""
        pass

    @abstractmethod
    def count_jobs(self, query: CountJobsQuery) -> int:
        """Returns number of jobs filtered by query"""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> DescribeJob:
        """Returns job record for a single job"""
        pass

    @abstractmethod
    def delete_job(self, job_id: str):
        """Deletes the job record, stops the job if running"""
        pass

    @abstractmethod
    def stop_job(self, job_id: str):
        """Stops the job, this is not analogous
        to the REST API that will be called to
        stop the job. Front end will call the PUT
        API with status update to STOPPED, which will
        call the update_job method. This method is
        supposed to do the work of actually stopping
        the process that is executing the job. In case
        of a task runner, you can assume a call to task
        runner to suspend the job.
        """
        pass

    @abstractmethod
    def create_job_definition(self, model: CreateJobDefinition) -> str:
        """Creates a new job definition record,
        consider this as the template for creating
        recurring/scheduled jobs.
        """
        pass

    @abstractmethod
    def update_job_definition(self, model: UpdateJob):
        """Updates job definition metadata in the persistence store,
        should only impact all future jobs.
        """
        pass

    @abstractmethod
    def delete_job_definition(self, job_definition_id: str):
        """Deletes the job definition record,
        implementors can optionally stop all running jobs
        """
        pass

    @abstractmethod
    def list_job_definitions(self, query: ListJobDefinitionsQuery) -> List[DescribeJobDefinition]:
        """Returns list of all job definitions filtered by query"""
        pass

    @abstractmethod
    def pause_jobs(self, job_definition_id: str):
        """Pauses all future jobs for a job definition"""
        pass


class Scheduler(BaseScheduler):

    _db_session = None

    def __init__(self, config: ExecutionConfig = {}):
        self.config = config

    @property
    def db_session(self):
        if not self._db_session:
            self._db_session = create_session(self.config.db_url)

        return self._db_session

    @property
    def execution_manager_class(self):
        return self.config.execution_manager_class

    def create_job(self, model: CreateJob) -> DescribeJob:
        with self.db_session() as session:
            job = Job(**model.dict(exclude_none=True))
            session.add(job)
            session.commit()

            p = Process(target=self.execution_manager_class(job.job_id, self.config).process)
            p.start()

            job.pid = p.pid
            session.commit()

            job_id = job.job_id

        return job_id

    def update_job(self, model: UpdateJob):
        with self.db_session() as session:
            session.query(Job).filter(Job.job_id == model.job_id).update(
                model.dict(exclude_none=True)
            )
            session.commit()

    def list_jobs(self, query: ListJobsQuery) -> ListJobsResponse:
        with self.db_session() as session:
            jobs = session.query(Job)

            if query.status:
                jobs = jobs.filter(Job.status == query.status)
            if query.job_definition_id:
                jobs = jobs.filter(Job.status == query.job_definition_id)
            if query.start_time:
                jobs = jobs.filter(Job.start_time >= query.start_time)
            if query.name:
                jobs = jobs.filter(Job.name.like(f"{query.name}%"))
            if query.tags:
                jobs = jobs.filter(and_(Job.tags.contains(tag) for tag in query.tags))

            total = jobs.count()

            if query.sort_by:
                for sort_field in query.sort_by:
                    direction = desc if sort_field.direction == SortDirection.desc else asc
                    jobs = jobs.order_by(direction(getattr(Job, sort_field.name)))
            next_token = int(query.next_token) if query.next_token else 0
            jobs = jobs.limit(query.max_items).offset(next_token)

            jobs = jobs.all()

        next_token = next_token + len(jobs)
        if next_token >= total:
            next_token = None

        list_jobs_response = ListJobsResponse(
            jobs=[DescribeJob.from_orm(job) for job in jobs or []], next_token=next_token
        )

        return list_jobs_response

    def count_jobs(self, query: CountJobsQuery) -> int:
        with self.db_session() as session:
            count = (
                session.query(func.count(Job.job_id)).filter(Job.status == query.status).scalar()
            )
            return count if count else 0

    def get_job(self, job_id: str) -> DescribeJob:
        with self.db_session() as session:
            job_record = session.query(Job).filter(Job.job_id == job_id).one()

            return DescribeJob.from_orm(job_record)

    def delete_job(self, job_id: str):
        with self.db_session() as session:
            job_record = session.query(Job).filter(Job.job_id == job_id).one()
            if Status(job_record.status) == Status.IN_PROGRESS:
                self.stop_job(job_id)

            session.query(Job).filter(Job.job_id == job_id).delete()
            session.commit()

    def stop_job(self, job_id):
        with self.db_session() as session:
            job_record = session.query(Job).filter(Job.job_id == job_id).one()
            job = DescribeJob.from_orm(job_record)
            process_id = job_record.pid
            if process_id and job.status == Status.IN_PROGRESS:
                session.query(Job).filter(Job.job_id == job_id).update({"status": Status.STOPPING})
                session.commit()

                current_process = psutil.Process()
                children = current_process.children(recursive=True)
                for proc in children:
                    if process_id == proc.pid:
                        proc.kill()
                        session.query(Job).filter(Job.job_id == job_id).update(
                            {"status": Status.STOPPED}
                        )
                        session.commit()
                        break

    def create_job_definition(self, model: CreateJobDefinition) -> str:
        pass

    def update_job_definition(self, model: UpdateJob):
        pass

    def delete_job_definition(self, job_definition_id: str):
        pass

    def list_job_definitions(self, query: ListJobDefinitionsQuery) -> List[DescribeJobDefinition]:
        pass

    def pause_jobs(self, job_definition_id: str):
        pass
