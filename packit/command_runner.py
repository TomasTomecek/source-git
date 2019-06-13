import logging
from typing import Dict, Type, List, Optional

from packit import utils
from packit.config import RunCommandType
from packit.exceptions import PackitConfigException
from packit.local_project import LocalProject

logger = logging.getLogger(__name__)


RUN_COMMAND_HANDLER_MAPPING: Dict[RunCommandType, Type["RunCommandHandler"]] = {}


def add_run_command(kls: Type["RunCommandHandler"]):
    RUN_COMMAND_HANDLER_MAPPING[kls.name] = kls
    return kls


class RunCommandHandler:
    """Generic interface to handle different run_commands"""

    name: RunCommandType

    def __init__(
        self,
        local_project: LocalProject,
        extra_kwargs: Optional[Dict],
        # cwd: str,
    ):
        """

        :param local_project:
        :param extra_kwargs:
        """
        self.local_project = local_project
        # self.cwd = cwd
        self.extra_kwargs = extra_kwargs or {}

    def run_command(self, command: List[str], return_output=True):
        raise NotImplementedError("This should be implemented")


@add_run_command
class LocalRunCommandHandler(RunCommandHandler):
    name = RunCommandType.local

    def run_command(self, command: List[str], return_output=True):
        """
        :param command: command to execute
        :param return_output: return output of the command if True
        """
        return utils.run_command(
            cmd=command, cwd=self.local_project.working_dir, output=return_output
        )


@add_run_command
class SandcastleRunCommandHandler(RunCommandHandler):
    name = RunCommandType.sandcastle

    def __init__(
        self,
        local_project: LocalProject,
        # cwd: str,
        extra_kwargs: Optional[Dict],
    ):
        """

        :param local_project:
        :param image_reference:
        :param k8s_namespace:
        :param extra_kwargs:
        """
        # we import here so that packit does not depend on sandcastle (and thus python-kube)
        from sandcastle.api import Sandcastle, MappedDir

        super().__init__(local_project, extra_kwargs)
        working_dir = "/tmp/work"
        m = MappedDir()
        m.path = working_dir
        m.local_dir = local_project.working_dir
        try:
            image_reference = extra_kwargs["image_reference"]
            k8s_namespace = extra_kwargs["k8s_namespace"]
        except KeyError:
            raise PackitConfigException(
                "image_reference and k8s_namespace need to be defined for sandcastle command runner"
            )
        self.sandcastle = Sandcastle(
            image_reference=image_reference,
            k8s_namespace_name=k8s_namespace,
            working_dir=working_dir,
            mapped_dirs=[m],
        )

    def run_command(self, command: List[str], return_output=True):
        """
        Executes command in VolumeMount directory
        :param command: command to execute
        :return: Output of command from sandcastle_object
        """
        if not self.sandcastle.is_pod_already_deployed():
            self.sandcastle.run()
        return self.sandcastle.exec(command=command)
