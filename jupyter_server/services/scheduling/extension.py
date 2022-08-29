from jupyter_server.extension.application import ExtensionApp

from jupyter_scheduling.orm import create_tables
from jupyter_scheduling.scheduler import Scheduler
from .handlers import BatchJobHandler, ConfigHandler, FeaturesHandler, JobDefinitionHandler, JobHandler, JobsCountHandler, RuntimeEnvironmentsHandler, CreateJobWithDefinitionHandler
from .environments import CondaEnvironmentManager
from .executors import DefaultExecutionManager

from jupyter_server.traittypes import TypeFromClasses
from jupyter_server.transutils import _i18n
from jupyter_core.paths import jupyter_data_dir
from traitlets import Unicode, Bool, default

from .config import ExecutionConfig


JOB_DEFINITION_ID_REGEX = r"(?P<job_definition_id>\w+-\w+-\w+-\w+-\w+)"
JOB_ID_REGEX = r"(?P<job_id>\w+-\w+-\w+-\w+-\w+)"

class SchedulerApp(ExtensionApp):
    name = "jupyter_scheduling"
    handlers = [
        (r"/job_definitions", JobDefinitionHandler),
        (r"/job_definitions/%s" % JOB_DEFINITION_ID_REGEX, JobDefinitionHandler),
        (r"/job_definitions/%s/jobs" % JOB_DEFINITION_ID_REGEX, CreateJobWithDefinitionHandler),
        (r"/jobs", JobHandler),
        (r"/jobs/count", JobsCountHandler),
        (r"/jobs/%s" % JOB_ID_REGEX, JobHandler),
        (r"/runtime_environments", RuntimeEnvironmentsHandler),
        (r"/scheduler/features", FeaturesHandler),
        (r"/scheduler/config", ConfigHandler),
        (r"/batch/jobs", BatchJobHandler)
    ]

    drop_tables = Bool(
        False, 
        config=True, 
        help="Drop the database tables before starting."
    )

    db_url = Unicode(
        config=True,
        help="URI for the scheduler database"
    )

    @default("db_url")
    def get_demo_db_url_default(self):
        return f"sqlite:///{jupyter_data_dir()}/scheduler.sqlite"

    environment_manager_class = TypeFromClasses(
        default_value=CondaEnvironmentManager,
        klasses=[
            "jupyter_scheduling.environments.EnvironmentManager"
        ],
        config=True,
        help=_i18n("The runtime environment manager class to use.")
    )


    execution_manager_class = TypeFromClasses(
        default_value=DefaultExecutionManager,
        klasses=[
            "jupyter_scheduling.executors.ExecutionManager"
        ],
        config=True,
        help=_i18n("The execution manager class to use.")
    )

    scheduler_class = TypeFromClasses(
        default_value=Scheduler,
        klasses=[
            "jupyter_scheduling.scheduler.BaseScheduler"
        ],
        config=True,
        help=_i18n("The scheduler class to use.")
    )

    def initialize_settings(self):
        super().initialize_settings()
        
        create_tables(self.db_url, self.drop_tables)
        
        self.settings.update(
            execution_config=ExecutionConfig(
                db_url=self.db_url,
                execution_manager_class=self.execution_manager_class,
                environments_manager_class=self.environment_manager_class,
                scheduler_class=self.scheduler_class,
                root_dir=self.settings.get("server_root_dir", None)
            )
        )