import json
import os
import subprocess
from abc import ABC, abstractmethod
from typing import List

from jupyter_scheduling.models import OutputFormat, RuntimeEnvironment


class EnvironmentManager(ABC):
    @abstractmethod
    def list_environments() -> List[RuntimeEnvironment]:
        pass

    @abstractmethod
    def manage_environments_command(self) -> str:
        pass


class CondaEnvironmentManager(EnvironmentManager):
    """Provides list of system installed conda environments"""

    def list_environments(self) -> List[RuntimeEnvironment]:
        environments = []

        try:
            envs = subprocess.check_output(["conda", "env", "list", "--json"])
            envs = json.loads(envs).get("envs", [])
        except subprocess.CalledProcessError as e:
            raise EnvironmentRetrievalError(e) from e

        for env in envs:
            name = os.path.basename(env)
            environments.append(
                RuntimeEnvironment(
                    name=name,
                    label=name,
                    description=f"Conda environment: {name}",
                    file_extensions=["ipynb", "py"],
                    output_formats=[
                        OutputFormat(name="ipynb", label="Notebook"),
                        OutputFormat(name="html", label="HTML"),
                    ],
                    metadata={"path": env},
                )
            )

        return environments

    def manage_environments_command(self) -> str:
        return ""


class StaticEnvironmentManager(EnvironmentManager):
    """Provides a static list of environments, for demo purpose only"""

    def list_environments(self) -> List[RuntimeEnvironment]:
        name = "jupyterlab-env"
        path = os.path.join(os.environ["HOME"], name)
        return [
            RuntimeEnvironment(
                name=name,
                label=name,
                description=f"Virtual environment: {name}",
                file_extensions=["ipynb", "py"],
                metadata={"path": path},
            )
        ]

    def manage_environments_command(self) -> str:
        return ""


class EnvironmentRetrievalError(Exception):
    pass
