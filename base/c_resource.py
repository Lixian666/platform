class CResource:
    Encoding_UTF8 = 'UTF-8'
    Encoding_GBK = 'GBK'
    Encoding_GB2312 = 'GB2312'
    Encoding_Chinese = 'GB18030'

    Port_Postgresql_Default = 5432

    Host_LocalHost = '127.0.0.1'

    OS_Windows = 'windows'
    OS_Linux = 'linux'
    OS_MacOS = 'Darwin'

    Docker_env = '/.dockerenv'

    DB_Server_ID_Default = '0'
    DB_True = -1
    DB_False = 0
    Not_Support = 1

    NAME_Params = 'params'

    Name_Name = 'name'
    Name_Directory = 'directory'
    Name_Password = 'password'
    Name_UserName = 'username'
    Name_Port = 'port'
    Name_Host = 'host'
    Name_Data = 'data'
    Name_Header = 'header'
    Name_Headers = 'headers'
    Name_ID = 'id'
    Name_Stream = 'stream'
    Name_Json = 'json'
    Name_Files = 'files'
    Name_Content_Type = 'content_type'
    Name_Mime_Type = 'mime_type'
    Name_Chunk_Size = 'chunk_size'
    Name_Dumps = 'dumps'
    Name_Redis = 'redis'
    Name_Server = 'server'
    Name_Client = 'client'
    Name_Url = 'url'
    Name_Timeout = 'timeout'
    Name_Parser = 'parser'
    Name_Service = 'service'
    Name_MultiSQL = 'multisql'
    Name_Version = 'version'
    Name_Thirdpart = 'thirdpart'
    Name_Settings = 'settings'
    Name_Log = 'log'
    Name_Path = 'path'
    Name_Level = 'level'
    Name_Include = 'include'
    Name_ON = 'on'
    Name_OFF = 'off'
    Name_Debug = 'debug'
    Name_Template = 'template'
    Name_Project = 'project'

    FileExt_Py = 'py'
    FileExt_Json = 'json'
    FileExt_TarGZ = 'tar.gz'
    FileExt_Zip = 'zip'

    FileType_Unknown = 'none'
    FileType_File = 'file'
    FileType_Dir = 'dir'

    Name_Application = 'application'
    Path_Setting_Application = Name_Application
    Path_Setting_Application_Dir = '{0}.{1}'.format(Path_Setting_Application, Name_Directory)
    Path_Setting_Application_Debug = '{0}.{1}'.format(Path_Setting_Application, Name_Debug)

    @classmethod
    def path_switch(cls, path_prefix, switch_name: str) -> str:
        return '{0}.{1}'.format(path_prefix, switch_name)