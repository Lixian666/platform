import logging
import sys

from base.c_file import CFile
from base.c_json import CJson
from base.c_os import COS
from base.c_resource import CResource
from base.c_utils import CUtils


class CSettings(CJson):
    def __init__(self, obj):
        super().__init__()
        self.__system_debug = False
        self._app_root_dir = ''
        self.load_obj(obj)
        self.auto_parser_include()
        self.init_environ()
        self.after_init()

    def system_debug(self) -> bool:
        return self.__system_debug

    def auto_parser_include(self):
        root_path = COS.environ().get('TSDB_HOME')
        if CUtils.equal_ignore_case(root_path, None):
            root_path = CFile.file_abs_path(CFile.join_file(CFile.file_path(CFile.unify(__file__)), '..', '..'))
            root_path = CFile.unify(root_path)

        if not CFile.file_or_path_exist(root_path):
            raise Exception('根路径[{0}]未找到, 无法初始化! '.format(root_path))

        app_name = CFile.file_name(root_path)
        self._app_root_dir = root_path
        config_path = CFile.join_file(root_path, CResource.Name_Version)
        # print(config_path)
        self.parser_include(config_path)
        self.set_app_information(self._app_root_dir, app_name)

    def set_app_information(self, app_dir, app_name):
        json_app = self.xpath_one(CResource.Path_Setting_Application, None)
        if json_app is None:
            self.set_value_of_name(
                CResource.Name_Application,
                {
                    CResource.Name_Name: app_name,
                    CResource.Name_Directory: app_dir
                }
            )
        else:
            json_app[CResource.Name_Name] = app_name
            json_app[CResource.Name_Directory] = app_dir
            self.set_value_of_name(CResource.Name_Application, json_app)

        self.init_sys_path()

    def init_sys_path(self):
        app_dir = self.xpath_one(CResource.Path_Setting_Application_Dir, None)
        if app_dir is not None:
            sys.path.append(app_dir)

    def set_logger(self, logger_path, logger_level=None):
        self.set_value_of_name(
            '{0}.{1}.{2}'.format(CResource.Name_Application, CResource.Name_Log, CResource.Name_Path),
            logger_path
        )

        if logger_level is not None:
            self.set_value_of_name(
                '{0}.{1}.{2}'.format(CResource.Name_Application, CResource.Name_Log, CResource.Name_Level),
                logger_level
            )

    def get_logger_level(self):
        return self.xpath_one(
            '{0}.{1}.{2}'.format(CResource.Name_Application, CResource.Name_Log, CResource.Name_Level),
            logging.ERROR
        )

    def get_logger_path(self):
        return self.xpath_one(
            '{0}.{1}.{2}'.format(CResource.Name_Application, CResource.Name_Log, CResource.Name_Path),
            None
        )

    def parser_include(self, include_file_path):
        include_node_list = self.xpath_one(CResource.Name_Include, None)
        if include_node_list is None:
            return

        new_settings_dict = dict()
        for include_node in include_node_list:
            if not CUtils.equal_ignore_case(CFile.file_ext(include_node), CResource.FileExt_Json):
                include_node = '{0}.{1}'.format(include_node, CResource.FileExt_Json)

            include_json_filename = CFile.join_file(include_file_path, CResource.Name_Project, include_node)
            if not CFile.file_or_path_exist(include_json_filename):
                include_json_filename = CFile.join_file(include_file_path, CResource.Name_Settings,
                                                        CResource.Name_Template, include_node)
            if not CFile.file_or_path_exist(include_json_filename):
                include_json_filename = CFile.join_file(include_file_path, CResource.Name_Settings,
                                                        CResource.Name_Debug, include_node)

            if not CFile.file_or_path_exist(include_json_filename):
                raise Exception('配置文件[{0}]未找到, 无法初始化! '.format(include_json_filename))

            include_settings_dict = CJson.from_file(include_json_filename).json_obj
            new_settings_dict = CUtils.dict_append_dict(new_settings_dict, include_settings_dict)

        self.load_obj(new_settings_dict)

    def init_environ(self):
        """
        初始化系统运行环境
        :return:
        """

        if COS.run_on_windows():
            # 初始化proj4运行环境
            COS.set_environ('PROJ_LIB', CFile.join_file(self._app_root_dir, 'thirdpart/gdal/proj_lib'))
            # 初始化gdal运行环境
            COS.set_environ('GDAL_DATA', CFile.join_file(self._app_root_dir, 'thirdpart/gdal/gdal_data'))
        COS.set_environ('GDAL_FILENAME_IS_UTF8', 'YES')
        COS.set_environ('SHAPE_ENCODING', 'UTF-8')
        # 此处注释是由于会对外部应用程序(如：生产线截图工具)的生成结果产生影响，导致生成结果异常(截图失败)
        # COS.set_environ('VSI_CACHE', 'TRUE')
        # COS.set_environ('VSI_CACHE_SIZE', '1000000')
        COS.set_environ('JPEGMEM', '1000000')

    def after_init(self):
        self.__system_debug = CUtils.equal_ignore_case(
            self.xpath_one(CResource.Path_Setting_Application_Debug, CResource.DB_False),
            CResource.DB_True
        )

    def switch_is_on(self, switch_path, switch_name, switch_default_status=None) -> bool:
        default_status = switch_default_status
        if default_status is None:
            default_status = CResource.Name_ON

        return CUtils.equal_ignore_case(
            self.xpath_one(
                CResource.path_switch(
                    switch_path,
                    switch_name
                ),
                default_status
            ),
            CResource.Name_ON
        )
