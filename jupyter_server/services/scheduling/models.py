from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel
from typing import Dict, List, Optional, Union



Tags = List[str]
ParameterValues = Union[int, str, float, bool]
EnvironmentParameterValues = Union[int, str, float, bool]

EMAIL_RE = ''
SCHEDULE_RE = ''



class OutputFormat(BaseModel):
    name: str
    label: str


class RuntimeEnvironment(BaseModel):
    name: str
    label: str
    description: str
    file_extensions: List[str]
    output_formats: List[OutputFormat]
    metadata: Optional[Dict[str, str]]

    def __str__(self):
        return self.json()


class EmailNotifications(BaseModel):
    on_start: Optional[List[str]]
    on_success: Optional[List[str]]
    on_failure: Optional[List[str]]
    no_alert_for_skipped_runs: bool = True

    def __str__(self) -> str:
        return self.json()


class Status(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"

    def __str__(self):
        return self.value

""" 
A string template to use for naming the output file,
this template will interpolate values from DescribeJob,
filename is a special variable, because there is no
matching attribute in DescribeJob, but probably the most
expected in the output filename. These templates are 
expecting jinja2 format for attributes. Attributes that
don't follow valid filenames will be normalized. 

Examples of other formats:
"{{name}}-{{timestamp}}"
"{{runtime_environment_name}}_{{filename}}_{{job_id}}" 
"""
OUTPUT_FILENAME_TEMPLATE = "{{filename}}-{{timestamp}}"


class CreateJob(BaseModel):
    input_uri: str
    output_prefix: str 
    runtime_environment_name: str
    runtime_environment_parameters: Optional[Dict[str, EnvironmentParameterValues]]
    output_formats: Optional[List[str]] = None
    idempotency_token: Optional[str] = None
    job_definition_id: Optional[str] = None
    parameters: Optional[Dict[str, ParameterValues]] = None
    tags: Optional[Tags] = None
    name: Optional[str] = None
    email_notifications: Optional[EmailNotifications] = None
    timeout_seconds: Optional[int] = 600
    retry_on_timeout: Optional[bool] = False
    max_retries: Optional[int] = 0
    min_retry_interval_millis: Optional[int] = 0
    output_filename_template: Optional[str] = OUTPUT_FILENAME_TEMPLATE
    compute_type: Optional[str] = None
    

class DescribeJob(CreateJob):
    job_id: str
    output_uri: str 
    url: str
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    status: Status = Status.STOPPED
    status_message: str = None

    class Config:
        orm_mode = True


class SortDirection(Enum):
    asc = "asc"
    desc = "desc"


class SortField(BaseModel):
    name: str
    direction: SortDirection


DEFAULT_SORT = SortField(
    name="start_time",
    direction=SortDirection.desc
)


class ListJobsQuery(BaseModel):
    job_definition_id: Optional[str] = None
    status: Optional[Status] = None
    name: Optional[str] = None
    start_time: Optional[int] = None
    tags: Optional[Tags] = None
    sort_by: List[SortField] = [DEFAULT_SORT]
    max_items: Optional[int] = 1000
    next_token: Optional[str] = None


class ListJobsResponse(BaseModel):
    jobs: List[DescribeJob] = []
    next_token: Optional[str] = None
    tags: Optional[str]
    sort_by: List[SortField] = None


class CountJobsQuery(BaseModel):
    status: Status = Status.IN_PROGRESS


class UpdateJob(BaseModel):
    job_id: str
    end_time: Optional[int] = None
    status: Optional[Status] = None
    status_message: str = None
    name: Optional[str] = None
    

class DeleteJob(BaseModel):
    job_id: str
    

class CreateJobDefinition(CreateJob): 
    schedule: Optional[str] = None
    timezone: Optional[str] = None


class DescribeJobDefinition(CreateJobDefinition):
    job_definition_id: str
    last_modified_time: int
    job_ids: List[str]


class UpdateJobDefinition(BaseModel):
    job_definition_id: str
    last_modified_time: Optional[int] = None
    schedule: Optional[str] = None
    input_uri: Optional[str] = None
    output_prefix: Optional[str] = None
    runtime_environment_name: Optional[str] = None
    idempotency_token: Optional[str] = None
    parameters: Optional[Dict[str, ParameterValues]] = None
    tags: Optional[Tags] = None
    name: Optional[str] = None
    email_notifications: Optional[EmailNotifications] = None
    timeout_seconds: Optional[int] = 600
    max_retries: Optional[int] = 0
    min_retry_interval_millis: Optional[int] = 0
    retry_on_timeout: Optional[bool] = False
    url: Optional[str] = None
    timezone: Optional[str] = None # Should be a timezone e.g., US/Eastern, Asia/Kolkata
    output_filename_template: Optional[str] = OUTPUT_FILENAME_TEMPLATE


class ListJobDefinitionsQuery(BaseModel):
    job_definition_id: str


class JobFeature(str, Enum):
    job_name = "job_name"
    parameters = "parameters"
    output_formats = "output_formats"
    job_definition = "job_definition"
    idempotency_token = "idempotency_token"
    tags = "tags"
    email_notifications = "email_notifications"
    timeout_seconds = "timeout_seconds"
    retry_on_timeout = "retry_on_timeout"
    max_retries = "max_retries"
    min_retry_interval_millis = "min_retry_interval_millis"
    output_filename_template = "output_filename_template"
    stop_job = "stop_job"
    delete_job  = "delete_job"
