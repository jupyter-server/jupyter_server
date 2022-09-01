from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionConfig:
    """
    Config values passed to the
    execution manager and scheduler
    """

    db_url: str
    root_dir: str
    execution_manager_class: any
    environments_manager_class: any
    scheduler_class: any
