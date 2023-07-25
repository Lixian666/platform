from __future__ import absolute_import

import glob
import os
import platform
import shutil
import stat
import time
from fnmatch import fnmatch
from typing import AnyStr

import chardet

from base.c_exceptions import PathNotCreateException
from base.c_os import COS
from base.c_resource import CResource
from base.c_utils import CUtils


class CFile:
    """
    文件操作工具类
    """
    unify_seperator = '/'
    MatchType_Common = 1
    MatchType_Regex = 2

    file_name_Maximum_length = 255

    __special_file_ext_list = ['tar.gz']

    def __init__(self):
        pass

    @classmethod
    def file_ext(cls, file_name_with_path: str) -> str:
        """获取文件后缀名

            Args:
                file_name_with_path: 文件全路径

            Returns:
                文件后缀名
        """
        file_name_tmp = CFile.file_name(file_name_with_path)
        file_main_name = CFile.file_main_name(file_name_with_path)
        if CUtils.equal_ignore_case(file_name_tmp, file_main_name):
            return ''

        file_ext = file_name_tmp.replace('{0}.'.format(file_main_name), '', 1)
        return file_ext

    @classmethod
    def sep(cls):
        """获取文件分割符

            Returns:
                文件分割符
        """
        return cls.unify_seperator

    @classmethod
    def file_name(cls, file_name_with_path: str) -> str:
        """获取文件名(带后缀名)

            Args:
                file_name_with_path: 文件全路径

            Returns:
                文件名
        """
        return os.path.basename(file_name_with_path)

    @classmethod
    def file_path(cls, file_name_with_path: str) -> str:
        """获取文件路径

            Args:
                file_name_with_path: 文件全路径

            Returns:
                文件路径
        """
        (input_file_path, input_file_main_name) = os.path.split(file_name_with_path)
        return input_file_path

    @classmethod
    def file_abs_path(cls, file_name_with_path: str) -> str:
        """获取文件绝对路径

            Args:
                file_name_with_path: 文件全路径

            Returns:
                文件绝对路径
        """
        file_name_with_path = cls.compatible_long_path(file_name_with_path)
        return os.path.abspath(file_name_with_path)

    @classmethod
    def file_main_name(cls, file_name_with_path: str):
        """获取文件名(不带后缀名)

            Args:
                file_name_with_path: 文件全路径

            Returns:
                文件名
        """
        filename_without_path = cls.file_name(file_name_with_path)

        for ext_white in cls.__special_file_ext_list:
            if filename_without_path.lower().endswith(ext_white.lower()):
                return filename_without_path[:len(filename_without_path) - len(ext_white) - 1]
        else:
            file_info = os.path.splitext(filename_without_path)
            return file_info[0]

    @classmethod
    def clear_file_ext(cls, file_name_with_path: str) -> str:
        """清理掉文件名中的扩展名

        Args:
            file_name_with_path: 带扩展名的文件名

        Returns: 无扩展名的文件名

        """
        return cls.join_file(cls.file_path(file_name_with_path), cls.file_main_name(file_name_with_path))

    @classmethod
    def change_file_ext(cls, file_name_with_path: str, file_ext: str):
        """改变文件的扩展名, 注意, 新扩展名不带前导点

        Args:
            file_name_with_path: 带扩展名的文件名
            file_ext: 改变的后缀名

        Returns:
            改变完的文件名

        """
        file_path = cls.file_path(file_name_with_path)
        file_main_name = '{0}.{1}'.format(cls.file_main_name(file_name_with_path), file_ext)
        if CUtils.equal_ignore_case(file_path, ''):
            return file_main_name
        else:
            return cls.join_file(file_path, file_main_name)

    @classmethod
    def check_and_create_directory(cls, file_name_with_path: str) -> bool:
        """检查并创建父目录，如果目录不存在则创建，最后返回目录是否存在的结果

            Args:
                file_name_with_path: 文件全路径

            Returns:
                目录是否存在的结果
        """
        return cls.check_and_create_directory_itself(cls.file_path(file_name_with_path))

    @classmethod
    def check_and_create_directory_itself(cls, file_path: str) -> bool:
        """检查并创建自身目录，如果自身目录不存在则创建，最后返回自身目录是否存在的结果

            Args:
                file_path: 文件路径

            Returns:
                自身目录是否存在的结果
        """
        try:
            if not os.path.exists(cls.compatible_long_path(file_path)):
                os.makedirs(cls.compatible_long_path(file_path))
            return cls.file_or_path_exist(file_path)
        except OSError as error:
            return False

    @classmethod
    def file_relation_path(cls, file_name_with_path: str, file_root_path: str) -> str:
        """获取文件相对路径

            Args:
                file_name_with_path: 文件全路径
                file_root_path: 文件根路径

            Returns:
                文件相对路径
        """
        if file_name_with_path.startswith(file_root_path):
            return file_name_with_path.replace(file_root_path, '', 1)
        else:
            return file_name_with_path

    @classmethod
    def file_or_subpath_of_path(cls, path: str, match_str: str = '*', match_type: int = MatchType_Common) -> list:
        """
            获取指定目录下的一级文件和子目录

            1. 可以支持常规检索和正则表达式检索
            2. 返回当前目录下的文件和子目录(不包含路径!!!)

            Args:
                path: 文件路径
                match_str: 匹配字符
                match_type: 匹配类型

            Returns:
                匹配到的文件列表
        """
        if not cls.file_or_path_exist(path):
            return []

        list_all_file = os.listdir(cls.compatible_long_path(path))
        if match_str == '*':
            return list_all_file
            # return SortedList(list_all_file)

        list_match_file = []
        for item_file_name in list_all_file:
            if cls.MatchType_Common == match_type:
                if cls.file_match(item_file_name, match_str):
                    list_match_file.append(item_file_name)
            else:
                if CUtils.text_match_re(item_file_name, match_str):
                    list_match_file.append(item_file_name)
        return list_match_file
        # return SortedList(list_match_file)

    @classmethod
    def find_file_or_subpath_of_path(cls, path: str, match_str: str, match_type: int = MatchType_Common) -> bool:
        """
            查询文件夹下是否存在匹配文件

            Args:
                path: 文件路径
                match_str: 匹配字符
                match_type: 匹配类型

            Returns:
                是否存在匹配文件
        """
        list_files = cls.file_or_subpath_of_path(path, match_str, match_type)
        return len(list_files) > 0

    @classmethod
    def join_file(cls, path: str, *paths: AnyStr) -> str:
        """进行文件路径的拼接

            Args:
                path: 文件路径
                *paths: 拼接路径

            Returns:
                拼接后的结果
        """
        result = CUtils.any_2_str(path).rstrip('/\\')
        for each_path in paths:
            real_file_name = CUtils.any_2_str(each_path)
            if real_file_name.startswith(r'/') or real_file_name.startswith('\\'):
                real_file_name = real_file_name[1:len(real_file_name)]
            if not CUtils.equal_ignore_case(real_file_name, ''):
                if not CUtils.equal_ignore_case(result, ''):
                    result = '{0}{1}{2}'.format(result, cls.sep(), real_file_name)
                else:
                    result = real_file_name
        return result

    @classmethod
    def add_prefix(cls, path: str) -> str:
        """进行文件路径的拼接

            Args:
                path: 文件路径

            Returns:
                拼接后的结果
        """
        real_path = CUtils.any_2_str(path)
        if real_path.startswith(r'/') or real_path.startswith('\\'):
            return real_path
        else:
            return '{0}{1}'.format(cls.sep(), real_path)

    @classmethod
    def unify(cls, file_or_path: str) -> str:
        """进行文件路径的连接符的转换

            Args:
                file_or_path: 文件路径

            Returns:
                转换后的结果
        """
        result = file_or_path
        result = result.replace('\\', cls.sep())
        return result

    @classmethod
    def remove_file(cls, file_name_with_path: str):
        """删除指定文件

            Args:
                file_name_with_path: 文件路径

            Returns:
                无返回结果
        """
        if cls.file_or_path_exist(file_name_with_path):
            os.remove(CFile.compatible_long_path(file_name_with_path))

    @classmethod
    def remove_dir(cls, file_path: str):
        """删除文件夹，同时删除文件夹下的文件和子文件夹

        Args:
            file_path: 文件夹路径

        Returns: 无

        """
        if cls.file_or_path_exist(file_path):
            # os.removedirs(file_path)
            shutil.rmtree(CFile.compatible_long_path(file_path))

    @classmethod
    def __find_matched_files(cls, root_path='.', match_text='*.*'):
        """查询当前目录下的文件

        Args:
            root_path: 文件夹路径
            match_text: 匹配字符

        Returns: 当前目录下的文件

        """
        for i in glob.glob(os.path.join(root_path, match_text)):
            yield i

    @classmethod
    def __find_all_matched_files(cls, root_path, match_text='*.*'):
        """查询当前目录下以及子目录的文件

        Args:
            root_path: 文件夹路径
            match_text: 匹配字符

        Returns: 当前目录下以及子目录的文件

        """
        for name in os.listdir(root_path):
            if os.path.isdir(os.path.join(root_path, name)):
                try:
                    for i in cls.__find_all_matched_files(os.path.join(root_path, name), match_text):
                        yield i
                except:
                    pass

        for i in cls.__find_matched_files(root_path, match_text):
            yield i

    @classmethod
    def remove_files(cls, root_path, match_text='*.*', recurse=False):
        """删除rootdir目录下以及子目录下符合的文件

        Args:
            root_path: 文件夹路径
            match_text: 匹配字符
            recurse: 是否删除子目录中的文件

        Returns: 无

        """
        if recurse:
            for i in cls.__find_all_matched_files(root_path, match_text):
                cls.remove_file(i)
        else:
            for i in cls.__find_matched_files(root_path, match_text):
                cls.remove_file(i)

    @classmethod
    def remove_dirs(cls, root_path, match_text='*'):
        """
        删除rootdir目录下所有子目录
        """
        for i in cls.__find_matched_files(root_path, match_text):
            cls.remove_dir(i)

    @classmethod
    def rename_file_or_dir(cls, old_file_name_with_path: str, new_file_name_with_path: str, clear_empty_dir=False):
        """
        重命名文件

        os.renames方法会在改名后清理空文件夹, 因此进行重写

        Args:
            old_file_name_with_path: 旧文件名
            new_file_name_with_path: 新文件名
            clear_empty_dir: 是否清楚空目录

        Returns: 无

        """
        old_file_name_with_path = cls.compatible_long_path(old_file_name_with_path)
        new_file_name_with_path = cls.compatible_long_path(new_file_name_with_path)

        if clear_empty_dir:
            os.renames(old_file_name_with_path, new_file_name_with_path)
        else:
            head, tail = os.path.split(new_file_name_with_path)
            if head and tail and not os.path.exists(head):
                os.makedirs(head)
            os.rename(old_file_name_with_path, new_file_name_with_path)

    @classmethod
    def file_time_format(cls, time_value: float, time_format_str: str = '%Y-%m-%d %H:%M:%S'):
        """格式化提取到的文件的时间字符

        Args:
            time_value: 时间字符
            time_format_str: 格式化字符串

        Returns: 格式化后的字符

        """
        return time.strftime(time_format_str, time.localtime(time_value))

    @classmethod
    def file_modify_time(cls, file_name_with_path: str, time_format_str: str = '%Y-%m-%d %H:%M:%S'):
        """获取文件修改时间

        Args:
            file_name_with_path: 文件路径
            time_format_str: 格式化字符串

        Returns: 文件修改时间

        """
        return time.strftime(time_format_str,
                             time.localtime(os.path.getmtime(cls.compatible_long_path(file_name_with_path))))

    @classmethod
    def file_create_time(cls, file_name_with_path: str, time_format_str: str = '%Y-%m-%d %H:%M:%S'):
        """获取文件创建时间

        Args:
            file_name_with_path: 文件路径
            time_format_str: 格式化字符串

        Returns: 文件创建时间

        """
        return time.strftime(time_format_str,
                             time.localtime(os.path.getctime(cls.compatible_long_path(file_name_with_path))))

    @classmethod
    def file_access_time(cls, file_name_with_path: str, time_format_str: str = '%Y-%m-%d %H:%M:%S'):
        """获取文件访问时间

        Args:
            file_name_with_path: 文件路径
            time_format_str: 格式化字符串

        Returns: 文件访问时间

        """
        return time.strftime(time_format_str,
                             time.localtime(os.path.getatime(cls.compatible_long_path(file_name_with_path))))

    @classmethod
    def file_size(cls, file_name_with_path: str) -> int:
        """获取文件大小

        Args:
            file_name_with_path: 文件路径

        Returns: 文件大小

        """
        return os.path.getsize(cls.compatible_long_path(file_name_with_path))

    @classmethod
    def is_file(cls, file_name_with_path: str) -> bool:
        """验证是否为文件

        Args:
            file_name_with_path: 文件路径

        Returns: 是否为文件

        """
        return os.path.isfile(cls.compatible_long_path(file_name_with_path))

    @classmethod
    def is_dir(cls, file_name_with_path: str) -> bool:
        """验证是否为目录

        Args:
            file_name_with_path: 文件路径

        Returns: 是否为目录

        """
        return os.path.isdir(cls.compatible_long_path(file_name_with_path))

    @classmethod
    def compatible_long_path(cls, file_name_with_path: str) -> str:
        """处理长路径问题，win系统中，路径过长会发生异常

        Args:
            file_name_with_path: 文件路径

        Returns: 处理后的路径

        """
        # if file_name_with_path is None or len(file_name_with_path) <= cls.file_name_Maximum_length:
        #     return file_name_with_path
        if file_name_with_path is None:
            return file_name_with_path

        if CUtils.equal_ignore_case(platform.system(), CResource.OS_Windows):
            # 增加绝对路径生成，因为'A/foo/../B'形式路径不被超长路径认可
            file_name_with_path = os.path.abspath(file_name_with_path)
            if file_name_with_path.startswith(r'\\?'):
                return file_name_with_path
            if file_name_with_path.startswith('//?/'):
                return file_name_with_path.replace(CFile.sep(), '\\')

            if file_name_with_path.startswith(r'\\'):
                file_name_with_path = file_name_with_path.replace(r'\\', '', 1)
                file_name_with_path = r'\\?\UNC\{0}'.format(file_name_with_path).replace(CFile.sep(), '\\')
            elif file_name_with_path.startswith(r'//'):
                file_name_with_path = file_name_with_path.replace(r'//', '', 1)
                file_name_with_path = r'\\?\UNC\{0}'.format(file_name_with_path).replace(CFile.sep(), '\\')
            else:
                file_name_with_path = r'\\?\{0}'.format(file_name_with_path).replace(CFile.sep(), '\\')
        return file_name_with_path

    @classmethod
    def rollback_compatible_long_path(cls, file_name_with_path: str) -> str:
        """回滚处理过的长路径，因为gdal不识别处理后的长路径

        Args:
            file_name_with_path: 文件路径

        Returns: 回滚后的路径

        """
        if file_name_with_path is None:
            return file_name_with_path

        if CUtils.equal_ignore_case(platform.system(), CResource.OS_Windows):
            if file_name_with_path.startswith('\\\\?\\UNC\\'):
                file_name_with_path = file_name_with_path.replace('\\\\?\\UNC\\', '\\\\', 1)
            elif file_name_with_path.startswith('\\\\?\\'):
                file_name_with_path = file_name_with_path.replace('\\\\?\\', '', 1)

        return file_name_with_path

    @classmethod
    def file_or_path_exist(cls, dir_name_with_path: str) -> bool:
        """验证文件或目录是否存在

        Args:
            dir_name_with_path: 文件路径

        Returns: 文件或目录是否存在

        """
        if dir_name_with_path is None:
            return False
        return os.path.exists(cls.compatible_long_path(dir_name_with_path))

    @classmethod
    def file_exist(cls, file_name_with_path: str) -> bool:
        """验证文件是否存在

        Args:
            file_name_with_path: 文件路径

        Returns: 文件是否存在

        """
        if file_name_with_path is None:
            return False
        return os.path.exists(cls.compatible_long_path(file_name_with_path)) and \
            os.path.isfile(cls.compatible_long_path(file_name_with_path))

    @classmethod
    def path_exist(cls, path_name_with_path: str) -> bool:
        """验证目录是否存在

        Args:
            path_name_with_path: 文件路径

        Returns: 目录是否存在

        """
        if path_name_with_path is None:
            return False
        return os.path.exists(cls.compatible_long_path(path_name_with_path)) and \
            os.path.isdir(cls.compatible_long_path(path_name_with_path))

    @classmethod
    def file_match(cls, file_name_with_path: str, pattern: str) -> bool:
        """进行文件名称匹配，使用win匹配字符模式

        Args:
            file_name_with_path: 文件路径
            pattern: 匹配字符

        Returns: 文件名称是否文件匹配

        """
        return fnmatch(file_name_with_path, pattern)

    @classmethod
    def file_match_list(cls, file_name_with_path: str, pattern_list) -> bool:
        """进行文件名称匹配, 匹配字符可为多个,使用win匹配字符模式

        Args:
            file_name_with_path: 文件路径
            pattern_list(list): 匹配字符

        Returns:
            文件名称是否文件匹配

        """
        if CUtils.equal_ignore_case(file_name_with_path, None):
            return True

        for pattern in pattern_list:
            if fnmatch(file_name_with_path, pattern):
                return True

        return False

    @classmethod
    def split(cls, p: AnyStr):
        """用于分割路径

        Args:
            p: 文件路径

        Returns:
            分割后的路径

        """
        return os.path.split(p)

    @classmethod
    def subpath_in_path(cls, sub_path: str, filepath: str) -> bool:
        """验证子路径是否存在于文件夹中

        Args:
            sub_path: 子文件路径
            filepath: 文件夹路径

        Returns:
            子路径是否存在于文件夹中

        """
        subpath_list = []
        file_path_str = filepath.replace("\\", "/")
        file_path_str, file_name_str = os.path.split(file_path_str)
        subpath_list.append(file_name_str.lower())
        while file_name_str != '':
            file_path_str, file_name_str = os.path.split(file_path_str)
            if file_name_str != '':
                subpath_list.append(file_name_str.lower())

        return subpath_list.count(sub_path.lower()) > 0

    @classmethod
    def identify_encoding(cls, text, default_encoding='UTF-8'):
        """文件的编码格式识别

        Args:
            text:需要转换的文本
            default_encoding:默认的编码格式

        Returns:
            str: 转换后的编码格式

        """
        identify_result = chardet.detect(text)
        identify_encoding = identify_result['encoding']
        # identify_probability = identify_result['confidence'] # 成功概率
        # 由于windows系统的编码有可能是Windows-1254,打印出来后还是乱码,所以不直接用UTF-8编码
        if CUtils.equal_ignore_case(identify_encoding, 'Windows-1254'):
            identify_encoding = 'UTF-8'
        if CUtils.equal_ignore_case(identify_encoding, ''):
            identify_encoding = default_encoding

        return identify_encoding

    @classmethod
    def file_2_str(cls, file_name_with_path: str, encoding=None) -> str:
        """提取文件内容并转换为字符串

        Args:
            file_name_with_path:文件路径
            encoding:默认的编码格式

        Returns:
            str: 文件内容

        """
        if not cls.file_or_path_exist(file_name_with_path):
            return ''

        f = open(cls.compatible_long_path(file_name_with_path), "rb")
        try:
            txt = f.read()
            if encoding is None:
                if len(txt) < 1000:
                    rt_encoding = cls.identify_encoding(txt)
                else:
                    rt_encoding = cls.identify_encoding(txt[:1000])
                    # 检查到前1000字符全是英文与数字, 识别为ascii, 但是后面字符存在中文, 导致中文缺失的情况, 因此扩展检查到1万字符
                    if CUtils.equal_ignore_case(rt_encoding, 'ascii'):
                        if len(txt) < 10000:
                            rt_encoding = cls.identify_encoding(txt)
                        else:
                            rt_encoding = cls.identify_encoding(txt[:10000])
            else:
                rt_encoding = encoding
            true_txt = txt.decode(rt_encoding, "ignore")
            return true_txt
        finally:
            f.close()

    @classmethod
    def str_2_file(cls, str_info: str, file_name_with_path: str, encoding_type='utf-8'):
        """用字符串生成文件

        Args:
            str_info:用于生产文件的字符串
            file_name_with_path:文件路径
            encoding_type:默认的编码格式

        Returns:
            无返回内容

        """
        if not CFile.check_and_create_directory(file_name_with_path):
            raise PathNotCreateException(file_name_with_path)

        if CUtils.equal_ignore_case(str_info, "") \
                or CUtils.equal_ignore_case(file_name_with_path, ""):
            return
        try:
            if CFile.check_and_create_directory(file_name_with_path):
                with open(file_name_with_path, "w", encoding=encoding_type) as f:
                    f.write(str_info)
        except Exception as error:
            print(error.__str__())

    @classmethod
    def file_2_list(cls, file_name_with_path: str) -> list:
        """提取文件内容并转换为字符串列表，按行分列表

        Args:
            file_name_with_path:文件路径

        Returns:
            list: 字符串列表

        """
        if not cls.file_or_path_exist(file_name_with_path):
            return None

        result = []
        f = open(file_name_with_path, "rb")
        try:
            txt_tem = f.read(1000)
            encoding = CFile.identify_encoding(txt_tem)
            f.seek(0)
            txt_list = f.readlines()
            for index, txt in enumerate(txt_list):
                txt = txt.decode(encoding, "ignore")
                result.append(CUtils.any_2_str(txt))
            return result
        finally:
            f.close()

    @classmethod
    def __file_or_dir_fullname_of_path_recurse(
            cls, result_file_fullname_list: [], path: str,
            is_recurse_subpath: bool = False, match_str: str = '*',
            match_type: int = MatchType_Common, is_recurse_subpath_all_file: bool = False):
        """私有方法，递归路径获取路径下的所有文件和文件夹的全文件名，仅供内部函数file_or_dir_fullname_of_path调用

        Args:
            result_file_fullname_list:结果文件列表，为文件全民
            path:文件路径
            is_recurse_subpath:是否匹配子路径（只能匹配父目录已匹配的子目录）
            match_str:匹配字符串
            match_type:匹配类型
            is_recurse_subpath_all_file:是否匹配子路径（全部匹配）

        Returns:
            无返回内容

        """
        list_file_name = cls.file_or_subpath_of_path(path, match_str, match_type)
        for file_name_temp in list_file_name:
            file_fullname_temp = cls.join_file(path, file_name_temp)
            result_file_fullname_list.append(file_fullname_temp)
            if is_recurse_subpath:
                if cls.is_dir(file_fullname_temp):
                    cls.__file_or_dir_fullname_of_path_recurse(
                        result_file_fullname_list, file_fullname_temp, is_recurse_subpath, match_str, match_type
                    )

        if is_recurse_subpath_all_file and (not is_recurse_subpath):
            list_all_file_name = cls.file_or_subpath_of_path(path)
            for all_file_name_temp in list_all_file_name:
                all_file_fullname_temp = cls.join_file(path, all_file_name_temp)
                if cls.is_dir(all_file_fullname_temp):
                    cls.__file_or_dir_fullname_of_path_recurse(
                        result_file_fullname_list, all_file_fullname_temp,
                        is_recurse_subpath, match_str, match_type, is_recurse_subpath_all_file
                    )

    @classmethod
    def file_or_dir_fullname_of_path(cls, path: str, is_recurse_subpath: bool = False, match_str: str = '*',
                                     match_type: int = MatchType_Common,
                                     is_recurse_subpath_all_file: bool = False) -> list:
        """公共方法：根据路径获取文件和文件夹的全文件名，根据参数is_recurse_subpath支持是否递归子目录

        Args:
            path: 扫描的目录
            is_recurse_subpath: 是否递归子目录（只能匹配父目录已匹配的子目录）
            match_str:匹配字符串
            match_type:匹配类型
            is_recurse_subpath_all_file:是否匹配子路径（全部匹配）

        Returns:
            匹配到的文件列表

        """
        list_file_fullname = []
        if cls.is_dir(path):
            cls.__file_or_dir_fullname_of_path_recurse(
                list_file_fullname, path, is_recurse_subpath, match_str, match_type, is_recurse_subpath_all_file
            )
        return list_file_fullname

    @classmethod
    def __stat_of_path(
            cls,
            path: str,
            is_recurse_subpath: bool,
            match_str: str,
            match_type: int,
            sub_dir_count: int,
            file_count: int,
            file_size_sum: int
    ):
        """私有方法：根据路径获取路径下的统计信息，根据参数is_recurse_subpath支持是否递归子目录

        Args:
            path: 扫描的目录
            is_recurse_subpath: 是否递归子目录
            match_str:匹配字符串
            match_type:匹配类型

        Returns:

            统计信息包括:

                1. 子目录个数
                2. 文件个数
                3. 文件总大小

        """
        result_sub_dir_count = sub_dir_count
        result_file_count = file_count
        result_file_size_sum = file_size_sum
        list_file_name = cls.file_or_subpath_of_path(path, match_str, match_type)
        for file_name_temp in list_file_name:
            file_fullname_temp = cls.join_file(path, file_name_temp)
            if cls.is_file(file_fullname_temp):
                result_file_count = result_file_count + 1
                result_file_size_sum = result_file_size_sum + cls.file_size(file_fullname_temp)
            else:
                result_sub_dir_count = result_sub_dir_count + 1
                if is_recurse_subpath:
                    result_sub_dir_count, result_file_count, result_file_size_sum = cls.__stat_of_path(
                        file_fullname_temp,
                        is_recurse_subpath,
                        match_str,
                        match_type,
                        result_sub_dir_count,
                        result_file_count,
                        result_file_size_sum
                    )
        return result_sub_dir_count, result_file_count, result_file_size_sum

    @classmethod
    def stat_of_path(cls, path: str, is_recurse_subpath: bool = False, match_str: str = '*',
                     match_type: int = MatchType_Common):
        """公共方法：根据路径获取路径下的统计信息，根据参数is_recurse_subpath支持是否递归子目录

        Args:
            path: 扫描的目录
            is_recurse_subpath: 是否递归子目录
            match_str:匹配字符串
            match_type:匹配类型

        Returns:

            统计信息包括:

                1. 子目录个数
                2. 文件个数
                3. 文件总大小

        """
        if cls.is_dir(path):
            return cls.__stat_of_path(path, is_recurse_subpath, match_str, match_type, 0, 0, 0)
        else:
            return 0, 1, cls.file_size(path)

    @classmethod
    def copy_file_to(cls, file_name_with_path: str, target_path: str):
        """复制文件到指定路径下

        Args:
            file_name_with_path: 文件路径
            target_path: 目标路径

        Returns: 无返回内容

        """
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        if cls.file_or_path_exist(file_name_with_path):
            if COS.run_on_windows():
                shutil.copy(cls.compatible_long_path(file_name_with_path), cls.compatible_long_path(target_path))
            else:
                # 在linux中，存在无操作权限的情况， 因此重构部分复制方法
                if cls.is_dir(target_path):
                    target_path = cls.join_file(target_path, cls.file_name(file_name_with_path))
                shutil.copyfile(cls.compatible_long_path(file_name_with_path), cls.compatible_long_path(target_path))
                # noinspection PyBroadException
                try:
                    shutil.copymode(
                        cls.compatible_long_path(file_name_with_path), cls.compatible_long_path(target_path)
                    )
                except Exception:
                    pass

    @classmethod
    def copy_path_to(cls, source_path: str, target_path: str):
        """复制文件夹到指定路径下

        Args:
            source_path: 文件夹路径
            target_path: 目标路径

        Returns: 无返回内容

        """
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        if cls.file_or_path_exist(source_path):
            # root 所指的是当前正在遍历的这个文件夹的本身的地址
            # dirs 是一个 list，内容是该文件夹中所有的目录的名字(不包括子目录)
            # files 同样是 list, 内容是该文件夹中所有的文件(不包括子目录)
            for root, dirs, files in os.walk(source_path):
                for file in files:
                    src_file = cls.join_file(root, file)
                    next_dir = cls.join_file(target_path, cls.file_relation_path(root, source_path))
                    cls.copy_file_to(src_file, next_dir)

    @classmethod
    def move_file_to(cls, file_name_with_path: str, target_path: str, new_file_name=None) -> bool:
        """移动文件到指定路径下

        Args:
            file_name_with_path: 文件路径
            target_path: 目标路径
            new_file_name: 移动后的文件名称

        Returns: 移动是否成功

        """
        if not cls.file_or_path_exist(target_path):
            if not cls.check_and_create_directory_itself(target_path):
                return False

        target_file_name = new_file_name
        if target_file_name is None:
            target_file_name = cls.file_name(file_name_with_path)

        target_file_with_path = cls.join_file(target_path, target_file_name)

        if cls.file_or_path_exist(file_name_with_path):
            try:
                # cls.make_writable(file_name_with_path)
                shutil.move(file_name_with_path, target_file_with_path)

                return cls.file_or_path_exist(target_file_with_path)
            except:
                try:
                    file_name_with_path = cls.compatible_long_path(file_name_with_path)
                    target_file_with_path_ori = target_file_with_path
                    target_file_with_path = cls.compatible_long_path(target_file_with_path)
                    shutil.move(file_name_with_path, target_file_with_path)
                    return cls.file_or_path_exist(target_file_with_path_ori)
                except:
                    return False

    @classmethod
    def make_tree_writable(cls, source_dir):
        """设置目录树的可读性

        Args:
            source_dir: 文件路径

        Returns: 无返回内容

        """
        for root, dirs, files in os.walk(source_dir):
            for name in files:
                cls.make_writable(cls.join_file(root, name))

    @classmethod
    def make_writable(cls, path_):
        """设置指定路径为可读

        Args:
            path_: 文件路径

        Returns: 无返回内容

        """
        os.chmod(path_, stat.S_IWUSR)

    @classmethod
    def make_tree_all_permission(cls, source_dir):
        cls.make_all_permission(source_dir)
        for root, dirs, files in os.walk(source_dir):
            for name in files:
                cls.make_all_permission(cls.join_file(root, name))
            for sub in dirs:
                cls.make_all_permission(cls.join_file(root, sub))

    @classmethod
    def make_all_permission(cls, path_):
        os.chmod(path_, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    @classmethod
    def move_path_to(cls, file_path: str, target_path: str):
        """
        移动源目录至目标目录

        注意: 是将源目录下的所有内容, 直接移动至目标目录下; 而不是将源目录作为子目录, 移动至目标目录下!!!

        Args:
            file_path: 文件路径
            target_path: 目标路径

        Returns:
            1. 是否完全正常移动: True/False
            2. 如果是错误, 则返回错误的文件列表, 是一个list

        """
        # 计算源目录的名称
        # cls.make_tree_writable(file_path)
        file_path_name = cls.file_name(file_path)
        target_path_full_name = cls.join_file(target_path, file_path_name)
        result, failure_list = cls.move_subpath_and_file_of_path_to(file_path, target_path_full_name)

        if len(failure_list) == 0:
            shutil.rmtree(CFile.compatible_long_path(file_path))

        return result, failure_list

    @classmethod
    def move_subpath_and_file_of_path_to(cls, file_path: str, target_path: str):
        """
        移动源目录下的子目录和文件, 至目标目录

        Args:
            file_path: 文件路径
            target_path: 目标路径

        Returns:
            1. 是否完全正常移动: True/False
            2. 如果是错误, 则返回错误的文件列表, 是一个list

        """
        failure_list = []

        if not cls.file_or_path_exist(target_path):
            if not cls.check_and_create_directory_itself(target_path):
                return False, failure_list

        for parent_path, sub_paths, sub_files in os.walk(file_path):
            relation_path = cls.file_relation_path(parent_path, file_path)
            for sub_file in sub_files:
                src_file = cls.join_file(parent_path, sub_file)
                if not cls.move_file_to(src_file, cls.join_file(target_path, relation_path)):
                    failure_list.append(cls.join_file(relation_path, sub_file))

        if len(failure_list) == 0:
            sub_path_list = cls.file_or_subpath_of_path(file_path)
            for sub_path in sub_path_list:
                sub_path_full_name = cls.join_file(file_path, sub_path)
                if cls.is_dir(sub_path_full_name):
                    shutil.rmtree(CFile.compatible_long_path(sub_path_full_name))

        return len(failure_list) == 0, failure_list

    @classmethod
    def file_locked(cls, file_name_with_path) -> bool:
        """
        检查文件是否被其他应用打开和锁定

        Args:
            file_name_with_path: 文件路径

        Returns:
            文件是否被其他应用打开和锁定

        """
        try:
            cls.rename_file_or_dir(file_name_with_path, '{0}_file_locked_test'.format(file_name_with_path))
            cls.rename_file_or_dir('{0}_file_locked_test'.format(file_name_with_path), file_name_with_path)
            return False
        except PermissionError:
            return True

    @classmethod
    def access(cls, file_or_path) -> bool:
        """
        检查文件是否可访问

        Args:
            file_or_path: 文件路径

        Returns:
            文件是否可访问

        """
        return os.access(file_or_path, os.F_OK)

    @classmethod
    def find_locked_file_in_path(cls, file_path) -> list:
        """
        检查文件夹下的子文件是否被其他应用打开和锁定

        Args:
            file_path: 文件路径

        Returns:
            文件夹下的子文件是否被其他应用打开和锁定

        """
        locked_file_list = []

        for parent_path, sub_paths, sub_files in os.walk(file_path):
            relation_path = cls.file_relation_path(parent_path, file_path)
            for sub_file in sub_files:
                src_file = cls.join_file(parent_path, sub_file)
                if cls.file_locked(src_file):
                    locked_file_list.append(cls.join_file(relation_path, sub_file))

        return locked_file_list

    @classmethod
    def move_file_or_dir_to(cls, file_path: str, target_path: str):
        """
        移动源目录或文件至目标目录

        注意: 是将源目录下的所有内容, 直接移动至目标目录下; 而不是将源目录作为子目录, 移动至目标目录下!!!

        Args:
            file_path: 文件路径
            target_path: 目标路径

        Returns:
            是否完全正常移动

        """
        if cls.is_dir(file_path):
            result, failure_list = cls.move_path_to(file_path, target_path)
            return result
        else:
            return cls.move_file_to(file_path, target_path)

    @classmethod
    def shutil_move_overwrite(cls, src, dst):
        """
        根据需求重写的移动方法, 注意本方法是移动为dst, 不是移动到dst, 并且如果文件已存在, 不论文件是什么都将直接覆盖!

        Args:
            src: 文件路径
            dst: 目标路径

        Returns:
            是否完全正常移动

        """
        src = cls.compatible_long_path(src)
        dst = cls.compatible_long_path(dst)

        if cls.is_dir(dst):
            if cls.is_samefile(src, dst):
                # 我们可能是在不区分大小写的文件系统上，无论如何都要执行重命名。
                cls.rename_file_or_dir(src, dst)
                # return True

        try:
            cls.rename_file_or_dir(src, dst)
        except OSError:
            if os.path.islink(src):
                # try:
                #     linkto = os.readlink(src)
                #     os.symlink(linkto, dst)
                # except:
                #     return False
                linkto = os.readlink(src)
                os.symlink(linkto, dst)

                try:
                    os.unlink(src)
                except:
                    pass

            elif cls.is_dir(src):
                # try:
                #     if cls.destinsrc(src, dst):
                #         return False
                #     shutil.copytree(src, dst, symlinks=True, dirs_exist_ok=True)
                # except:
                #     return False
                if cls.destinsrc(src, dst):
                    raise Exception("移动文件时发生错误，目标目录位于来源目录中，无法进行移动！")
                shutil.copytree(src, dst, symlinks=True, dirs_exist_ok=True)

                try:
                    shutil.rmtree(src)
                except:
                    pass

            else:
                # try:
                #     shutil.copyfile(src, dst, follow_symlinks=True)
                #     shutil.copystat(src, dst, follow_symlinks=True)
                # except:
                #     return False
                shutil.copyfile(src, dst, follow_symlinks=True)
                shutil.copystat(src, dst, follow_symlinks=True)

                try:
                    os.unlink(src)
                except:
                    pass

    @classmethod
    def is_samefile(cls, src: str, dst: str):
        """
        此方法可以验证相对路径与绝对路径的是否为统一文件

        Args:
            src: 源文件路径
            dst: 目标文件路径

        Returns:
            是否为统一文件

        """
        # Macintosh, Unix.
        if isinstance(src, os.DirEntry) and hasattr(os.path, 'samestat'):
            try:
                return os.path.samestat(src.stat(), os.stat(dst))
            except OSError:
                return False

        if hasattr(os.path, 'samefile'):
            try:
                return os.path.samefile(src, dst)
            except OSError:
                return False

        # All other platforms: check for same pathname.
        return os.path.normcase(os.path.abspath(src)) == os.path.normcase(os.path.abspath(dst))

    @classmethod
    def destinsrc(cls, src: str, dst: str):
        """
        判定dst是否在src中

        Args:
            src: 源文件路径
            dst: 目标文件路径

        Returns:
            dst是否在src中

        """
        src = os.path.abspath(src)
        dst = os.path.abspath(dst)
        if not src.endswith(os.path.sep):
            src += os.path.sep
        if not dst.endswith(os.path.sep):
            dst += os.path.sep
        return dst.startswith(src)

    @classmethod
    def __file_or_subpath_of_path_recurse(cls, result_file_fullname_list: [], path: str, match_str: str = '*',
                                          match_type: int = MatchType_Common, full_path=False):
        """私有方法，递归路径获取路径下的所有文件和文件夹的全文件名，仅供内部函数file_or_subpath_of_path_recurse调用

        Args:
            result_file_fullname_list:结果文件列表，为文件全民
            path:文件路径
            match_str:匹配字符串
            match_type:匹配类型
            full_path:结果是否要为全路径

        Returns:
            无返回内容

        """
        if full_path:
            file_main_name_with_ext = cls.file_or_subpath_of_path(path, match_str, match_type)
            result_file_fullname_list.extend(
                [CFile.join_file(path, file_name) for file_name in file_main_name_with_ext]
            )
        else:
            result_file_fullname_list.extend(
                cls.file_or_subpath_of_path(path, match_str, match_type)
            )

        list_all_file_name = cls.file_or_subpath_of_path(path)
        for all_file_name_temp in list_all_file_name:
            all_file_fullname_temp = cls.join_file(path, all_file_name_temp)
            if cls.is_dir(all_file_fullname_temp):
                cls.__file_or_subpath_of_path_recurse(
                    result_file_fullname_list, all_file_fullname_temp, match_str, match_type, full_path
                )

    @classmethod
    def file_or_subpath_of_path_recurse(cls, path: str, match_str: str = '*',
                                        match_type: int = MatchType_Common, full_path=False):
        """公共方法：根据路径递归子目录获取文件和文件夹的全文件名

        Args:
            path: 扫描的目录
            match_str:匹配字符串
            match_type:匹配类型
            full_path:结果是否要为全路径

        Returns:
            匹配到的文件列表

        """
        list_file_fullname = []
        if cls.is_dir(path):
            cls.__file_or_subpath_of_path_recurse(list_file_fullname, path, match_str, match_type, full_path)
        return list_file_fullname

    @classmethod
    def listdir(cls, path):
        """获取文件夹下所有文件

            Args:
                path: 文件夹路径

            Returns:
                获取到的文件列表

        """
        path = cls.rollback_compatible_long_path(path)
        return os.listdir(path)

    @classmethod
    def walk(cls, path):
        """遍历文件夹下所有文件

            Args:
                path: 文件夹路径

            Returns:
                遍历到的文件列表

        """
        return os.walk(path)

    @classmethod
    def __search_one(cls, path_list, match_str: str = '*', match_type: int = MatchType_Common):
        """通过正则匹配检索一个目录下指定的目录或者文件夹, 检索到一个之后直接退出, 返回值是一个name_with_path的str

            Args:
                path_list: 文件夹路径
                match_str: 匹配字符串
                match_type: 匹配类型

            Returns:
                匹配到的文件

        """
        extends_paths = []
        for path in path_list:
            if cls.is_dir(path):
                if cls.find_file_or_subpath_of_path(path, match_str, match_type):
                    return cls.join_file(path, cls.file_or_subpath_of_path(path, match_str, match_type)[0])
                else:
                    next_names_with_path = cls.file_or_dir_fullname_of_path(path)
                    for next_name_with_path in next_names_with_path:
                        if cls.is_dir(next_name_with_path):
                            extends_paths.append(next_name_with_path)
        if len(extends_paths) == 0:
            return None
        return cls.__search_one(extends_paths, match_str, match_type)

    @classmethod
    def search_one(cls, path: str, match_str: str = '*', match_type: int = MatchType_Common):
        """通过正则匹配检索一个目录下指定的目录或者文件夹, 检索到一个之后直接退出, 返回值是一个name_with_path的str

            Args:
                path: 文件夹路径
                match_str: 匹配字符串
                match_type: 匹配类型

            Returns:
                匹配到的文件

        """
        extends_paths = []
        if cls.is_dir(path):
            if cls.find_file_or_subpath_of_path(path, match_str, match_type):
                return cls.join_file(path, cls.file_or_subpath_of_path(path, match_str, match_type)[0])
            else:
                next_names_with_path = cls.file_or_dir_fullname_of_path(path)
                for next_name_with_path in next_names_with_path:
                    if cls.is_dir(next_name_with_path):
                        extends_paths.append(next_name_with_path)
        return cls.__search_one(extends_paths, match_str, match_type)

    @classmethod
    def check_empty_dir(cls, path) -> bool:
        """检查文件夹是否为空文件夹

            Args:
                path: 文件夹路径

            Returns:
                是否为空文件夹

        """
        sub_dir_list = cls.listdir(path)
        for sub_dir in sub_dir_list:
            sub_dir_full_path = cls.join_file(path, sub_dir)
            if cls.is_dir(sub_dir_full_path):
                empty_dir_flag = cls.check_empty_dir(sub_dir_full_path)
                if not empty_dir_flag:
                    return False
            else:
                return False

        return True
