"""
内容: JSON对象操作封装
1.每一个方法均可用
2.每一个方法均支持中文, 包括但不限于
  中文路径
  中文标签名称
  中文标签文本
  中文属性名称
  中文属性值
"""

from __future__ import absolute_import

import demjson
import jsonpath

from base.c_exceptions import PathNotCreateException
from base.c_file import CFile
from base.c_http import CHttp
from base.c_utils import CUtils

# noinspection PyBroadException
try:
    import ujson
except Exception:
    pass


class CJson:
    Encoding_UTF8 = 'UTF-8'
    Encoding_GBK = 'GB2312'

    __json_obj = None

    # 使用ensure_ascii=false输出UTF-8
    __ensure_ascii = False

    def __init__(self):
        self.__json_obj = dict()

    def load_file(self, filename):
        """
        通过给定的json文件名, 对json对象进行初始化
        :param filename:
        :return:
        """
        if CFile.file_or_path_exist(filename):
            file_content = CFile.file_2_str(filename)
            self.load_json_text(file_content)

    def load_url(self, url):
        """
        通过给定的url地址, 对Json对象进行初始化
        :param url:
        :return:
        """
        url_data = CHttp.get(url)
        if url_data is not None:
            self.load_json_text(url_data)
        else:
            self.load_json_text('{}')

    def load_json_text(self, json_content: str):
        """
        通过给定的json内容, 对json对象进行初始化
        :param json_content:
        :return:
        """
        if CUtils.is_str(json_content):
            rt_json_content = CUtils.any_2_str(json_content)
            if rt_json_content is None:
                rt_json_content = '{}'
            elif rt_json_content == '':
                rt_json_content = '{}'

            # noinspection PyBroadException
            try:
                self.__json_obj = ujson.loads(rt_json_content)
            except Exception:
                # 因为demjson包的接口较强, 所以使用demjson包进行字典转换
                self.__json_obj = demjson.decode(rt_json_content)
                # noinspection PyBroadException
                try:
                    # 因为demjson包转换出的字典存在Decimal函数字典, 无法序列化, 再用ujson转一遍
                    self.__json_obj = ujson.loads(ujson.dumps(self.__json_obj, ensure_ascii=self.__ensure_ascii))
                except Exception:
                    pass
        else:
            self.load_obj(json_content)

    def load_obj(self, obj):
        """
        通过给定的json内容, 对json对象进行初始化
        :param obj:
        :return:
        """
        if CUtils.is_dict(obj):
            # 稳定性保证
            # noinspection PyBroadException
            try:
                temp_obj = ujson.dumps(obj, ensure_ascii=self.__ensure_ascii)
            except Exception:
                temp_obj = demjson.encode(obj)

            self.load_json_text(temp_obj)
        else:
            self.load_json_text(CUtils.any_2_str(obj))

    @classmethod
    def from_obj(cls, obj):
        result = CJson()
        if obj is None:
            return result

        if CUtils.is_str(obj):
            result.load_json_text(obj)
        else:
            result.load_obj(obj)
        return result

    @classmethod
    def from_url(cls, url):
        result = CJson()
        result.load_url(url)
        return result

    @classmethod
    def from_file(cls, filename):
        result = CJson()
        result.load_file(filename)
        return result

    def to_json(self, indent=0) -> str:
        # noinspection PyBroadException
        try:
            return ujson.dumps(self.__json_obj, ensure_ascii=self.__ensure_ascii, indent=indent)
        except Exception:
            return demjson.encode(self.__json_obj)

    def to_file(self, filename):
        if not CFile.check_and_create_directory(filename):
            raise PathNotCreateException(CFile.file_path(filename))
        str_info = self.to_json()
        CFile.str_2_file(str_info, filename)

    def set_value_of_name(self, name, value):
        name_str = CUtils.any_2_str(name)
        if name_str.find('.') == -1:
            if isinstance(self.__json_obj, list):
                self.__json_obj[int(name)] = value
            else:
                self.__json_obj[name] = value
        else:
            name_key_next_key = name_str.split('.', 1)
            name_key = name_key_next_key[0]
            name_next_key = name_key_next_key[1]

            json_obj_new = CJson()
            name_key_value = self.xpath_one(name_key, None)
            if name_key_value is not None:
                json_obj_new.load_obj(name_key_value)
            json_obj_new.set_value_of_name(name_next_key, value)

            if isinstance(self.__json_obj, list):
                self.__json_obj[int(name_key)] = json_obj_new.json_obj
            else:
                self.__json_obj[name_key] = json_obj_new.json_obj

    @property
    def json_obj(self):
        return self.__json_obj

    def xpath_one(self, query, attr_value_default) -> any:
        """
        根据给定的xpath查询语句, 查询出合适的节点
        :param query:
        :param attr_value_default:
        :return:
        """
        result_list = self.xpath(query)
        if len(result_list) == 0:
            return attr_value_default
        elif len(result_list) >= 1:
            return result_list[0]

    def xpath(self, query) -> list:
        """
        获取一个属性的值, 如果属性不存在, 则返回默认值
        :param query:
        :return:
        """
        result_list = jsonpath.jsonpath(self.__json_obj, query)
        if not result_list:
            return []
        else:
            return result_list

    @classmethod
    def json_path(cls, json_text, json_path_str: str) -> list:
        """
        获取一个属性的值, 如果属性不存在, 则返回默认值
        1. 如果json_text不是合法的json格式, 将反馈空列表, 而不是None
        :param json_path_str:
        :param json_text:
        :return:
        """
        if json_text is None:
            return []
        elif str(json_text) == '':
            return []
        else:
            json = CJson()
            try:
                json.load_json_text(json_text)
                return json.xpath(json_path_str)
            except Exception as err:
                return []

    @classmethod
    def json_path_one(cls, json_text, json_path_str: str, attr_value_default) -> any:
        """
        获取一个属性的值, 如果属性不存在, 则返回默认值
        1. 如果json_text不是合法的json格式, 将反馈空列表, 而不是None
        :param attr_value_default:
        :param json_path_str:
        :param json_text:
        :return:
        """
        if json_text is None:
            return attr_value_default
        elif CUtils.any_2_str(json_text) == '':
            return attr_value_default
        else:
            json = CJson()
            try:
                json.load_json_text(json_text)
                return json.xpath_one(json_path_str, attr_value_default)
            except:
                return attr_value_default

    @classmethod
    def json_attr_value(cls, json_text, json_path_str: str, attr_value_default) -> any:
        """
        获取一个属性的值, 如果属性不存在, 则返回默认值

        :param json_path_str:
        :param json_text:
        :param attr_value_default:
        :return:
        """
        if json_text is None:
            return attr_value_default
        elif str(json_text) == '':
            return attr_value_default
        else:
            json = CJson()
            try:
                json.load_json_text(json_text)
                return json.xpath_one(json_path_str, attr_value_default)
            except Exception as err:
                return attr_value_default

    @classmethod
    def json_set_attr(cls, json_text, attr_name: str, attr_value) -> str:
        new_result = CJson()
        rt_json_text = CUtils.any_2_str(json_text)
        if not CUtils.equal_ignore_case(rt_json_text, ''):
            new_result.load_json_text(rt_json_text)

        new_result.set_value_of_name(attr_name, attr_value)
        return new_result.to_json()

    @classmethod
    def json_join(cls, json_path: str, *json_suffix) -> str:
        result_path = json_path
        for suffix in json_suffix:
            result_path = '{0}.{1}'.format(result_path, suffix)
        return result_path

    @classmethod
    def file_2_str(cls, filename) -> str:
        json = CJson()
        json.load_file(filename)
        return json.to_json()

    @classmethod
    def str_2_file(cls, json_content, filename: str):
        if not CFile.check_and_create_directory(filename):
            raise PathNotCreateException(filename)

        json = CJson()
        if CUtils.is_str(json_content):
            json.load_json_text(CUtils.any_2_str(json_content))
        else:
            json.load_obj(json_content)

        json.to_file(filename)

    @classmethod
    def dict_data_by_path(cls, obj: dict, path_str: str) -> list:
        """
        将一个字典对象, 按json解析, 并以指定的path获取其中的对象

        :param path_str:
        :param obj:
        :return:
        """
        if obj is None:
            return []
        elif str(obj) == '':
            return []
        else:
            json = CJson()
            try:
                json.load_obj(obj)
                return json.xpath(path_str)
            except Exception as err:
                return []

    @classmethod
    def dict_attr_by_path(cls, obj: dict, path_str: str, attr_value_default=None):
        """
        将一个字典对象, 按json解析, 并以指定的path获取其中的对象

        :param attr_value_default:
        :param path_str:
        :param obj:
        :return:
        """
        if obj is None:
            return attr_value_default
        elif str(obj) == '':
            return attr_value_default
        else:
            json = CJson()
            try:
                json.load_obj(obj)
                return json.xpath_one(path_str, attr_value_default)
            except Exception as err:
                return attr_value_default

    @classmethod
    def dict_2_json(cls, dict_or_text) -> str:
        if CUtils.equal_ignore_case(dict_or_text, ''):
            return None
        else:
            new_json_object = CJson()
            new_json_object.load_json_text(dict_or_text)
            return new_json_object.to_json()


if __name__ == '__main__':
    json_obj = CJson.from_file('d:/*.json')
    tool_obj = json_obj.xpath_one('tool', None)
    tools = CUtils.dict_keys(tool_obj)
    for tool in tools:
        print(tool)
