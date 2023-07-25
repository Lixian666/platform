class FileException(Exception):
    """
    文件异常异常类
    """
    _file_name: None

    def __init__(self, file_name):
        super().__init__()
        self._file_name = file_name


class DBException(Exception):
    """
    数据库不存在异常类
    """

    def __init__(self, db_id):
        self.__db_id__ = db_id


class DBLinkException(DBException):
    """
    数据库连接失异常类
    """

    def __str__(self):
        return "标示为[{0}]的数据库连接失败, 请检查数据库连接参数是否正确! ".format(self.__db_id__)


class PathNotCreateException(FileException):
    """
    路径无法创建异常类
    """

    def __init__(self, file_name):
        self.__file_name__ = file_name

    def __str__(self):
        return "目录[{0}]无法创建!".format(self._file_name)
