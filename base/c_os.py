import os
import platform

from base.c_resource import CResource
from base.c_utils import CUtils


class COS(CResource):
    @classmethod
    def get_platform_system_name(cls):
        return platform.system()

    @classmethod
    def run_on_windows(cls):
        return CUtils.equal_ignore_case(cls.get_platform_system_name(), cls.OS_Windows)

    @classmethod
    def run_on_docker(cls):
        return os.path.exists(cls.Docker_env)

    @classmethod
    def get_execute_process_id(cls):
        return os.getpid()

    @classmethod
    def get_os_name(cls):
        return os.name

    @classmethod
    def environ(cls):
        return os.environ

    @classmethod
    def set_environ(cls, name, value):
        os.environ[name] = CUtils.any_2_str(value)

    @classmethod
    def get_python_version(cls, level: int = 0):
        if CUtils.equal_ignore_case(level, 0):
            return platform.python_version()
        elif CUtils.equal_ignore_case(level, 1):
            return platform.python_version()[:platform.python_version().find('.')]
        elif CUtils.equal_ignore_case(level, 2):
            return platform.python_version()[:platform.python_version().rfind('.')]
        else:
            return None
