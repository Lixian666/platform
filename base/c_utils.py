from __future__ import absolute_import

import hashlib
import math
import re
import uuid
from datetime import datetime
from string import Template
from urllib import parse

from base.c_resource import CResource
from base.c_time import CTime


class CUtils(CResource):
    @classmethod
    def str_append(cls, src_str: str, second_str: str, seperator_str: str = '\n') -> str:
        result = cls.any_2_str(src_str)
        if second_str == '':
            return result

        if result != '':
            result = '{0}{1}'.format(result, seperator_str)

        return '{0}{1}'.format(result, second_str)

    @classmethod
    def one_id(cls) -> str:
        name = 'metadata.org'
        uuid_text = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(uuid.uuid4())))
        uuid_text = 'at_' + uuid_text.replace('-', '')
        return uuid_text

    @classmethod
    def to_md5(cls, text) -> str:
        # postgres默认使用u8进行编码, 所以这里也一样
        # 使用本方式时留心text的编码问题, 更建议用数据库的md5
        text = text.encode(encoding=cls.Encoding_UTF8)
        return hashlib.new('md5', text).hexdigest()

    @classmethod
    def plugins_id_by_file_main_name(cls, file_main_name) -> str:
        super_id = file_main_name
        id_list = super_id.split('_', 2)
        if len(id_list) > 2:
            return id_list[2]
        else:
            return super_id

    @classmethod
    def replace_placeholder(cls, text: str, dict_obj: dict, safe: bool = True) -> str:
        """
        按照Python的Template规范进行占位符的替换
        占位符格式如下:
        . $name
        . ${$name}
        具体百度python template
        如果字符串里需要$, 则使用$$消除占位语法

        :param text:
        :param dict_obj:
        :param safe:
        :return:
        """
        if dict_obj is None:
            return text

        if safe:
            return Template(text).safe_substitute(dict_obj)
        else:
            return Template(text).substitute(dict_obj)

    @classmethod
    def replace_placeholder_own(cls, text: str, dict_obj: dict, safe: bool = True) -> str:
        """
        按照Python的Template规范进行占位符的替换
        占位符格式如下:
        . $name
        . ${$name}
        具体百度python template
        如果字符串里需要$, 则使用$$消除占位语法
        """
        if dict_obj is None or len(dict_obj) == 0:
            return text

        # 保证不会地址传递
        result = text[:]

        dict_keys = cls.dict_keys(dict_obj)
        params_list = cls.findall_of_regular(r'\$\{(.*?)\}', CUtils.any_2_str(text))

        for param_name in params_list:
            if CUtils.list_exists(dict_keys, param_name):
                result = CUtils.replace(
                    result, '${%s}' % CUtils.any_2_str(param_name), cls.dict_value_by_name(dict_obj, param_name, '')
                )
            elif not safe:
                result = CUtils.replace(result, '${%s}' % CUtils.any_2_str(param_name), '')

        return result

    @classmethod
    def replace_of_regular(cls, text: str, regular: str, repl: str = '', count=0) -> str:
        """
        使用正则表达式替换字符串
        :param text:字符串
        :param regular:正则
        :param repl:被替换的字符串
        :param count:被替换的字符串
        :return:
        """
        if regular is None:
            return text
        return re.sub(regular, cls.any_2_str(repl), cls.any_2_str(text), count)

    @classmethod
    def startswith(cls, text, prefix, start=None, end=None):
        if prefix is None:
            return False
        else:
            return cls.any_2_str(text).startswith(prefix, start, end)

    @classmethod
    def endswith(cls, text, prefix, start=None, end=None):
        if prefix is None:
            return False
        else:
            return cls.any_2_str(text).endswith(prefix, start, end)

    @classmethod
    def replace(cls, text, old_str: str, new_str: str, max_count=-1) -> str:
        """
        替换字符串
        :param text:字符串
        :param old_str:正则
        :param new_str:被替换的字符串
        :param max_count:最大替换数
        :return:
        """
        result = cls.any_2_str(text)
        if max_count >= 0:
            return result.replace(cls.any_2_str(old_str), cls.any_2_str(new_str), max_count)
        else:
            return result.replace(cls.any_2_str(old_str), cls.any_2_str(new_str))

    @classmethod
    def equal_ignore_case(cls, str1, str2) -> bool:
        return cls.any_2_str(str1).strip().lower() == cls.any_2_str(str2).strip().lower()

    @classmethod
    def quote(cls, str1: str) -> str:
        return "'{0}'".format(cls.any_2_str(str1))

    @classmethod
    def str_find(cls, text: str, find_str: str) -> bool:
        rt_str1 = cls.any_2_str(text).lower()
        rt_find_str = cls.any_2_str(find_str).lower()
        position = rt_str1.find(rt_find_str)
        return position >= 0

    @classmethod
    def dict_xpath(cls, dict_obj: dict, path: str, default_value) -> any:
        if dict_obj is None:
            return default_value

        if not cls.is_dict(dict_obj):
            return default_value

        result = dict_obj
        path_list = cls.split(path, ['.'], False)
        for item in path_list:
            if not cls.is_dict(result):
                return default_value

            result = cls.dict_value_by_name(result, item, None)
            if result is None:
                return default_value
        return result

    @classmethod
    def dict_value_by_name(cls, dict_obj: dict, name: str, default_value: object, ignore_case: object = True) -> any:
        if dict_obj is None:
            return default_value

        keys = dict_obj.keys()
        for key in keys:
            if ignore_case:
                if cls.equal_ignore_case(key, name):
                    return dict_obj[key]
            else:
                if key.strip() == name.strip():
                    return dict_obj[key]
        else:
            return default_value

    @classmethod
    def dict_set_value(cls, dict_obj: dict, name: str, value) -> dict:
        result = dict(dict_obj)
        name_str = CUtils.any_2_str(name)
        if name_str.find('.') == -1:
            result[name_str] = value
        else:
            name_key_next_key = name_str.split('.', 1)
            name_key = name_key_next_key[0]
            name_next_key = name_key_next_key[1]

            name_key_value = cls.dict_value_by_name(result, name_key, None)
            if name_key_value is None:
                name_key_value = dict()
            name_key_value = cls.dict_set_value(name_key_value, name_next_key, value)
            result[name_key] = name_key_value
        return result

    @classmethod
    def dict_2_str(cls, dict_obj, seperator: str) -> any:
        result = ''
        if dict_obj is None:
            return result

        keys = dict_obj.keys()
        for key in keys:
            value = cls.any_2_str(dict_obj[key])
            result = cls.str_append(result, value, seperator)
        return result

    @classmethod
    def dict_2_key_str(cls, dict_obj, seperator: str) -> any:
        result = ''
        if dict_obj is None:
            return result

        keys = dict_obj.keys()
        for key in keys:
            value = cls.any_2_str(dict_obj[key])
            key_and_value = '{0}:{1}'.format(key, value)
            result = cls.str_append(result, key_and_value, seperator)
        return result

    @classmethod
    def list_count(cls, list_obj: list, name: str, ignore_case=True) -> int:
        if list_obj is None:
            return 0
        elif not ignore_case:
            return list_obj.count(name)
        else:
            result_int = 0
            for list_item in list_obj:
                if cls.equal_ignore_case(cls.any_2_str(list_item), name):
                    result_int = result_int + 1
            return result_int

    @classmethod
    def list_index_of(cls, list_obj: list, name: str, ignore_case=True) -> int:
        if list_obj is None:
            return -1
        elif not ignore_case:
            return list_obj.index(name)
        else:
            for result_int in range(len(list_obj)):
                list_item = list_obj[result_int]
                if cls.equal_ignore_case(cls.any_2_str(list_item), name):
                    return result_int
            return -1

    @classmethod
    def list_exists(cls, list_obj: list, name: str, ignore_case=True) -> bool:
        if list_obj is None:
            return False
        elif not ignore_case:
            try:
                list_obj.index(name)
                return True
            except:
                return False
        else:
            for list_item in list_obj:
                if cls.equal_ignore_case(cls.any_2_str(list_item), name):
                    return True
            return False

    @classmethod
    def list_2_str(cls, list_obj: list, prefix: str, separator: str, suffix: str, ignore_empty: bool = False) -> str:
        if list_obj is None:
            return ''
        elif len(list_obj) == 0:
            return ''
        else:
            result = None
            for list_item in list_obj:
                list_text = cls.any_2_str(list_item)
                if ignore_empty:
                    if cls.equal_ignore_case(list_text, ''):
                        continue
                    result = cls.str_append(
                        result,
                        '{0}{1}{2}'.format(prefix, list_text, suffix),
                        separator
                    )
                else:
                    if result is None:
                        result = '{0}{1}{2}'.format(prefix, list_text, suffix)
                    else:
                        result = '{0}{1}{2}'.format(
                            result,
                            separator,
                            '{0}{1}{2}'.format(prefix, list_text, suffix)
                        )
            return result

    @classmethod
    def any_2_str(cls, obj) -> str:
        if obj is None:
            return ''
        else:
            try:
                return str(obj)
            except:
                obj_text = obj.encode(cls.Encoding_Chinese)
                return str(obj_text)

    @classmethod
    def int_2_format_str(cls, int_value: int, length: int, fill_str: str = '0') -> str:
        rt_int_value = int_value
        if rt_int_value is None:
            rt_int_value = 1

        str_value = cls.any_2_str(rt_int_value)
        if len(str_value) >= length:
            return str(str_value)
        else:
            count_zero = length - len(str_value)
            str_zero = fill_str * count_zero
            return '{0}{1}'.format(str_zero, str_value)

    @classmethod
    def type_name_of(cls, obj) -> str:
        if obj is None:
            return ''
        else:
            return type(obj).__name__

    @classmethod
    def type_is(cls, obj, type_name) -> bool:
        if obj is None:
            return False
        else:
            return cls.equal_ignore_case(cls.type_name_of(obj), type_name)

    @classmethod
    def is_list(cls, obj) -> bool:
        if obj is None:
            return False
        else:
            return cls.equal_ignore_case(cls.type_name_of(obj), cls.Python_ObjType_List)

    @classmethod
    def is_dict(cls, obj) -> bool:
        if obj is None:
            return False
        else:
            return cls.equal_ignore_case(cls.type_name_of(obj), cls.Python_ObjType_Dict)

    @classmethod
    def is_str(cls, obj) -> bool:
        if obj is None:
            return False
        else:
            return cls.equal_ignore_case(cls.type_name_of(obj), cls.Python_ObjType_Str)

    @classmethod
    def text_match_re(cls, text, regex) -> bool:
        try:
            return re.search(regex, text) is not None
        except:
            return False

    @classmethod
    def check_value_range(cls, value, ranges: list):
        """
         判断数字的范围，如经纬度坐标值：（-180 ~ 180） （-90~90）
        """
        if CUtils.equal_ignore_case(value, ''):
            return False
        default_value = -1.000001
        range_max = CUtils.to_decimal(ranges[1])
        range_min = CUtils.to_decimal(ranges[0])

        value_real = CUtils.to_decimal(value, -1)

        if range_max != default_value and range_min != default_value:
            if range_min <= value_real <= range_max:
                return True
            else:
                return False
        elif range_min != default_value:
            if range_min <= value_real:
                return True
            else:
                return False
        elif range_max != default_value:
            if range_max >= value_real:
                return True
            else:
                return False
        else:
            return True

    @classmethod
    def text_is_numeric(cls, check_text: str) -> bool:
        """
        判断是否为纯数字（不带负号，不带.符号）
        :param check_text:
        :return:
        """
        return check_text.isdigit()

    @classmethod
    def text_is_date(cls, check_text: str) -> bool:
        """
        判断是否为年月日,或年月,或年（不包含时间），如2020,202010,2020/10,2020-10 或20201022,2020/10/22,2020-10-22
        @param check_text:
        @return:
        """
        new_check_text = cls.any_2_str(check_text).replace(' ', '')
        if cls.text_is_date_day(new_check_text):
            return True
        elif cls.text_is_date_month(new_check_text):
            return True
        elif cls.text_is_date_year(new_check_text):
            return True
        return False

    @classmethod
    def text_is_date_day(cls, check_text: str) -> bool:
        """
        判断是否为年月日（不包含时间），如20201022,2020/10/22,2020-10-22,2020.10.22,2020年10月22日
        @param check_text:
        @return:
        """
        # 日期格式最低8位
        if CUtils.len_of_text(check_text) < 8:
            return False
        time_format = "%Y{0}%m{0}%d"
        sep_real = ""
        sep_list = ['-', '/']
        for sep in sep_list:
            if sep in check_text:
                sep_real = sep
                break
        time_format_real = time_format.format(sep_real)
        default_date = CTime.now()
        date_value = CTime.from_datetime_str(check_text, default_date, time_format_real)
        if CUtils.equal_ignore_case(date_value, default_date):
            return False
        return True

    @classmethod
    def text_is_date_month(cls, check_text: str) -> bool:
        """
        判断是否为年月（不包含日），如202010,2020/10,2020-10
        @param check_text:
        @return:
        """
        time_format = "%Y{0}%m"
        sep_real = ""
        sep_list = ['-', '/']
        for sep in sep_list:
            if sep in check_text:
                sep_real = sep
                break
        time_format_real = time_format.format(sep_real)
        default_date = CTime.now()
        date_value = CTime.from_datetime_str(check_text, default_date, time_format_real)
        if CUtils.equal_ignore_case(date_value, default_date):
            return False
        return True

    @classmethod
    def text_is_date_month_nosep(cls, check_text: str) -> bool:
        """
        判断时间类型(只有月份，并且没有‘-’or‘/’，例如YYYYMM)
        """
        sep_list = ['-', '/']
        for sep in sep_list:
            if sep in check_text:
                return False
        if CUtils.text_is_date_month(check_text):
            return True
        return False

    @classmethod
    def text_is_date_year(cls, check_text: str) -> bool:
        """
        判断是否为年（不包含月日），如2020
        @param check_text:
        @return:
        """
        time_format = "%Y"
        default_date = CTime.now()
        date_value = CTime.from_datetime_str(check_text, default_date, time_format)
        if CUtils.equal_ignore_case(date_value, default_date):
            return False
        return True

    @classmethod
    def text_is_datetime(cls, check_text: str) -> bool:
        """
        判断是否为日期时间（包含时间），如20201022 22:22:22.345,
        2020/10/22 22:22:22.345, 2020-10-22 22:22:22.345, 2020-10-22T22:22:22.000007
        @param check_text:
        @return:
        """
        time_format = "%Y{0}%m{0}%d{1}%H{2}%M{2}%S{3}{4}"
        sep_real = ""
        sep_list = ['-', '/']
        for sep in sep_list:
            if sep in check_text:
                sep_real = sep
                break
        # 判断是否带T，GMT
        sign_real = ""
        check_text = check_text.replace(' ', '')
        sign_list = ['T', 'CST']
        for sign in sign_list:
            if sign in check_text:
                sign_real = sign
                break

        colon_real = ""
        if ":" in check_text:
            colon_real = ":"
        second_real = ""
        if "." in check_text:
            second_real = ".%f"
        z_real = ""
        if "Z" in check_text:
            z_real = "Z"

        time_format_real = time_format.format(sep_real, sign_real, colon_real, second_real, z_real)
        default_date = CTime.now()
        date_value = CTime.from_datetime_str(check_text, default_date, time_format_real)
        if CUtils.equal_ignore_case(date_value, default_date):
            return False
        return True

    @classmethod
    def text_is_date_or_datetime(cls, check_text: str) -> bool:
        """
        判断是否为日期或日期时间），如20201022,2020/10/22,2020-10-22，
            20201022 22:22:22.345,2020/10/22 22:22:22.345,2020-10-22 22:22:22.345, 2020-10-22T22:22:22.000007
        @param check_text:
        @return:
        """
        if cls.text_is_date(check_text):
            return True
        elif cls.text_is_datetime(check_text):
            return True
        return False

    @classmethod
    def standard_datetime_sql_format(cls, date_text: str) -> str:
        """
        将日期或日期时间格式化为YYYYMMDD HHMMSS.AA格式，如20201022020202.22格式化为20201022020202.22
        @param date_text:
        @return:
        """
        resource_date_text = date_text
        sep_list = [' ', '-', '/']
        # for sep in sep_list:
        #     if sep in date_text:
        #         date_text = date_text.replace(sep, '')
        # date_text_list = list(date_text)
        # date_text_list.insert(8, ' ')
        # date_text = ''.join(date_text_list)
        # if cls.text_is_date_or_datetime(date_text):
        #     return date_text
        # else:
        data_text_list = CUtils.split(resource_date_text, sep_list)
        if len(data_text_list) > 2:
            if len(data_text_list[1]) == 1:
                data_text_list[1] = '0{0}'.format(data_text_list[1])
            if len(data_text_list[2]) == 1:
                data_text_list[2] = '0{0}'.format(data_text_list[2])
            data_text_list.insert(3, ' ')
            date_text = ''
            for index in range(len(data_text_list)):
                date_text = '{0}{1}'.format(date_text, data_text_list[index])
        if date_text is not None:
            return date_text.strip()
        return date_text

    @classmethod
    def standard_datetime_format(cls, date_text: str, default_date) -> datetime:
        """
        将日期或日期时间格式化为YYYY-MM-DD HH:MM:SS格式，如20201022,2020/10/22格式化为2020-10-22，
            20201022 22:22:22.345,2020/10/22 22:22:22.345格式化为2020-10-22 22:22:22.345, 2020-10-22T22:22:22.000007
        @param date_text:
        @param default_date:  CTime.now()
        @return:
        """
        # default_date = CTime.now()
        try:
            time_format_real = '%Y-%m-%d %H:%M:%S'
            time_format = ["%Y{0}", "%Y{0}%m{1}", "%Y{0}%m{1}%d{2}{3}%H:%M:%S{4}", "%Y{0}%m{1}%d{2}", "%Y",
                           "%Y{0}%m", "%Y{0}%m{0}%d{1}%H:%M:%S{2}", "%Y{0}%m{0}%d"]

            date_text = cls.any_2_str(date_text)
            str_len = len(date_text)

            # 汉字标记
            ch_flag = 0
            if ('年' in date_text) or ('月' in date_text) or ('日' in date_text):
                ch_flag = 1

            # 日期时间标记
            sign_flag = 0
            sign_list = ['T', 'CST', ' ']
            for sign in sign_list:
                if sign in date_text:
                    sign_flag = 1
                    break

            if ch_flag:
                if str_len == 5:
                    time_format_real = time_format[0].format('年')
                    date_value = CTime.from_datetime_str(date_text, default_date, time_format_real)
                    if CUtils.equal_ignore_case(date_value, default_date):
                        return default_date
                    return CTime.format_str(date_value, '%Y')
                elif (str_len == 7) or (str_len == 8):
                    time_format_real = time_format[1].format('年', '月')
                    date_value = CTime.from_datetime_str(date_text, default_date, time_format_real)
                    if CUtils.equal_ignore_case(date_value, default_date):
                        return default_date
                    return CTime.format_str(date_value, '%Y-%m')
                elif str_len >= 9:
                    if sign_flag:
                        sign_real = " "
                        sign_list = ['CST', 'T']
                        for sign in sign_list:
                            if sign in date_text:
                                sign_real = sign
                                break
                        sec_real = ""
                        if "." in date_text:
                            sec_real = ".%f"
                        time_format_real = time_format[2].format('年', '月', '日', sign_real, sec_real)
                        date_value = CTime.from_datetime_str(date_text, default_date, time_format_real)
                        if CUtils.equal_ignore_case(date_value, default_date):
                            return default_date
                        return CTime.format_str(date_value, '%Y-%m-%d %H:%M:%S')
                    else:
                        time_format_real = time_format[3].format('年', '月', '日')
                    date_value = CTime.from_datetime_str(date_text, default_date, time_format_real)
                    if CUtils.equal_ignore_case(date_value, default_date):
                        return default_date
                    return CTime.format_str(date_value, '%Y-%m-%d')
            else:
                if str_len == 4:
                    time_format_real = time_format[4]
                    date_value = CTime.from_datetime_str(date_text, default_date, time_format_real)
                    if CUtils.equal_ignore_case(date_value, default_date):
                        return default_date
                    return CTime.format_str(date_value, '%Y')
                elif (str_len == 6) or (str_len == 7):
                    sep_real = ""
                    sep_list = ['-', '/', '.']
                    for sep in sep_list:
                        if sep in date_text:
                            sep_real = sep
                            break
                    time_format_real = time_format[5].format(sep_real)
                    date_value = CTime.from_datetime_str(date_text, default_date, time_format_real)
                    if CUtils.equal_ignore_case(date_value, default_date):
                        return default_date
                    return CTime.format_str(date_value, '%Y-%m')
                elif str_len >= 8:
                    if sign_flag:
                        sign_real = " "
                        sign_list = ['CST', 'T']
                        for sign in sign_list:
                            if sign in date_text:
                                sign_real = sign
                                break
                        date, time = date_text.split(sign_real)
                        sep_real = ""
                        sep_list = ['-', '/', '.']
                        for sep in sep_list:
                            if sep in date:
                                sep_real = sep
                                break
                        sec_real = ""
                        if "." in time:
                            sec_real = ".%f"
                        time_format_real = time_format[6].format(sep_real, sign_real, sec_real)
                        date_value = CTime.from_datetime_str(date_text, default_date, time_format_real)
                        if CUtils.equal_ignore_case(date_value, default_date):
                            return default_date
                        return CTime.format_str(date_value, '%Y-%m-%d %H:%M:%S')
                    else:
                        sep_real = ""
                        sep_list = ['-', '/', '.']
                        for sep in sep_list:
                            if sep in date_text:
                                sep_real = sep
                                break
                        time_format_real = time_format[7].format(sep_real)
                        date_value = CTime.from_datetime_str(date_text, default_date, time_format_real)
                        if CUtils.equal_ignore_case(date_value, default_date):
                            return default_date
                        return CTime.format_str(date_value, '%Y-%m-%d')

        except:
            return default_date

    @classmethod
    def text_is_decimal(cls, check_text: str) -> bool:
        """
        判断是否为小数，（必须有小数点，包含正小数，负小数，不包含整数）
            1.小数点个数可以使用.count()方法
            2.按照小数点进行分割 例如： 1.98 [1,98]
            3.正小数：小数点左边是整数，右边也是整数 可以使用.isdigits()方法
            4.负小数：小数点左边是是负号开头，但是只有一个负号，右边也是整数
        :param check_text:
        :return:
        """
        check_text = cls.any_2_str(check_text)
        check_text_list = None
        if check_text.count(".") == 1:  # 小数点个数
            check_text_list = check_text.split(".")
        if check_text_list is None:
            return False
        left = check_text_list[0]  # 小数点左边
        right = check_text_list[1]  # 小数点右边
        if left.isdigit() and right.isdigit():
            return True
        elif left.startswith('-') and left.count('-') == 1 and left.split('-')[1].isdigit() and right.isdigit():
            return True
        return False

    @classmethod
    def text_is_integer(cls, check_text: str) -> bool:
        """
        判断是否为整数（包含正负整数，不带.符号）
        :param check_text:
        :return:
        """
        try:
            temp_value = int(check_text)
            return isinstance(temp_value, int)
        except ValueError:
            return False

    @classmethod
    def text_is_decimal_or_integer(cls, check_text: str) -> bool:
        """
        判断是否为小数或整数（包含负数）
        :param check_text:
        :return:
        """
        if cls.text_is_decimal(check_text):
            return True
        elif cls.text_is_integer(check_text):
            return True
        return False

    @classmethod
    def text_is_decimal_or_integer_positive(cls, check_text: str) -> bool:
        """
        判断是否为正小数或整数（不包含负数）
        :param check_text:
        :return:
        """
        if cls.text_is_decimal_or_integer(check_text):
            value_num = float(check_text)
            if value_num > 0:
                return True
        return False

    @classmethod
    def text_is_alpha(cls, check_text: str) -> bool:
        """
        判断是否字母
        :param check_text:
        :return:
        """
        return check_text.isalpha()

    @classmethod
    def text_is_string(cls, obj):
        """
        判断是否是字符串文本
        @param obj:
        @return:
        """
        return isinstance(obj, str)

    @classmethod
    def len_of_text(cls, text_obj):
        """
        获取文本或数字类型的长度
        @param text_obj:
        @return:
        """
        value_str = CUtils.any_2_str(text_obj)
        len_text = len(value_str)
        return len_text

    @classmethod
    def to_decimal(cls, obj, default_value=-1):
        """
        文本转小数
        @param obj:
        @param default_value:
        @return:
        """
        if CUtils.equal_ignore_case(obj, ''):
            return default_value
        try:
            value = float(obj)
            return value
        except:
            return default_value

    @classmethod
    def to_integer(cls, obj, default_value=-1):
        """
        文本转整数
        @param obj:
        @param default_value:
        @return:
        """
        if CUtils.equal_ignore_case(obj, ''):
            return default_value
        try:
            value_decimal = cls.to_decimal(obj, default_value)
            value = int(value_decimal)
            return value
        except:
            return default_value

    @classmethod
    def to_integer_of_ceil(cls, obj, default_value=-1):
        """
        文本转整数并向上取整
        @param obj:
        @param default_value:
        @return:
        """
        if CUtils.equal_ignore_case(obj, ''):
            return default_value
        try:
            value_decimal = cls.to_decimal(obj, default_value)
            value = int(math.ceil(value_decimal))
            return value
        except:
            return default_value

    @classmethod
    def text_to_lower(cls, text):
        """
        文本转小写
        @param text:
        @return:
        """
        if text is not None:
            return text.lower()
        return text

    @classmethod
    def to_day_format(cls, text, default_value):
        """
        文本转日（只对年、月转换），日不用转，只会格式化,
            2020  2020年  转为 20200101
            202009 2020-09 2020/09  2020年9月   转为20200901
        @param text:
        @param default_value:
        @return:
        """
        # default_date = CTime.now()
        date_value = cls.standard_datetime_format(text, default_value)
        if CUtils.equal_ignore_case(date_value, default_value) or CUtils.equal_ignore_case(date_value, ''):
            return default_value
        date_value = CUtils.any_2_str(date_value)
        date_value = date_value.replace('-', '')
        day_format = ''
        if CUtils.len_of_text(date_value) == 4:
            day_format = '{0}0101'.format(date_value)
        elif CUtils.len_of_text(date_value) == 6:
            day_format = '{0}01'.format(date_value)
        else:
            day_format = date_value
        return day_format

    @classmethod
    def to_day_and_time_format(cls, text, default_value):
        """
        YYYY-MM-DD HH:MM:SS.%f时间文本转YYYY-MM-DD HH:MM:SS（只对年、月转换），日不用转，只会格式化,
            2020  2020年  转为 20200101
            202009 2020-09 2020/09  2020年9月   转为20200901
        @param text:
        @param default_value:
        @return:
        """
        text = text.split('.')[0]
        time_format = "%Y{0}%m{0}%d{1}%H{2}%M{2}%S"
        sep_real = ""
        sep_list = ['-', '/']
        for sep in sep_list:
            if sep in text:
                sep_real = sep
                break
        # 判断是否带T，GMT
        sign_real = ""
        check_text = text.replace(' ', '')
        sign_list = ['T', 'CST']
        for sign in sign_list:
            if sign in check_text:
                sign_real = sign
                break

        colon_real = ""
        if ":" in check_text:
            colon_real = ":"

        time_format_real = time_format.format(sep_real, sign_real, colon_real)
        default_date = CTime.now()
        date_value = CTime.from_datetime_str(check_text, default_date, time_format_real)
        if CUtils.equal_ignore_case(date_value, default_date):
            return str(default_date)
        return str(date_value)

    @classmethod
    def list_clear_empty_string(cls, list_obj: list) -> list:
        result_list = []
        if list_obj is None:
            return []
        if len(list_obj) == 0:
            return []
        for list_item in list_obj:
            if not cls.equal_ignore_case(None, list_item):
                result_list.append(list_item)
        return result_list

    @classmethod
    def list_clear_same_string(cls, list_obj: list) -> list:
        result_list = []
        if list_obj is None:
            return []
        if len(list_obj) == 0:
            return []
        for list_item in list_obj:
            if not cls.list_exists(result_list, list_item):
                result_list.append(list_item)
        return result_list

    @classmethod
    def split(cls, split_text: str, split_sep_list: list, include_empty_str: bool = True) -> list:
        """
        根据指定的分隔符数组, 对指定文本进行分割
        :param split_text:
        :param split_sep_list:
        :param include_empty_str:
        :return:
        """
        if cls.equal_ignore_case(split_text, None):
            return []

        if split_sep_list is None:
            return [split_text]

        if len(split_sep_list) == 0:
            return [split_text]

        text_part_list = [split_text]
        for index in range(len(split_sep_list)):
            result_list = cls.__split_list(text_part_list, split_sep_list[index], include_empty_str)
            text_part_list = result_list
        return text_part_list

    @classmethod
    def __split_list(cls, text_part_list: list, split_sep: str, include_empty_str: bool = True) -> list:
        """
        私有方法：根据分割的文本段数组、分隔符获取分割后的结果集合
        @param text_part_list:
        @param split_sep:
        @return:
        """
        result_list = []
        for text_item in text_part_list:
            text_part_list2 = text_item.split(split_sep)
            for item in text_part_list2:
                if (not include_empty_str) and cls.equal_ignore_case(item, ''):
                    continue

                result_list.append(item)
        return result_list

    @classmethod
    def __single_get_first(cls, text):
        str1 = text.encode(cls.Encoding_Chinese)
        try:
            ord(str1)
            return text
        except:
            asc = str1[0] * 256 + str1[1] - 65536
            if asc >= -20319 and asc <= -20284:
                return 'a'
            if asc >= -20283 and asc <= -19776:
                return 'b'
            if asc >= -19775 and asc <= -19219:
                return 'c'
            if asc >= -19218 and asc <= -18711:
                return 'd'
            if asc >= -18710 and asc <= -18527:
                return 'e'
            if asc >= -18526 and asc <= -18240:
                return 'f'
            if asc >= -18239 and asc <= -17923:
                return 'g'
            if asc >= -17922 and asc <= -17418:
                return 'h'
            if asc >= -17417 and asc <= -16475:
                return 'j'
            if asc >= -16474 and asc <= -16213:
                return 'k'
            if asc >= -16212 and asc <= -15641:
                return 'l'
            if asc >= -15640 and asc <= -15166:
                return 'm'
            if asc >= -15165 and asc <= -14923:
                return 'n'
            if asc >= -14922 and asc <= -14915:
                return 'o'
            if asc >= -14914 and asc <= -14631:
                return 'p'
            if asc >= -14630 and asc <= -14150:
                return 'q'
            if asc >= -14149 and asc <= -14091:
                return 'r'
            if asc >= -14090 and asc <= -13119:
                return 's'
            if asc >= -13118 and asc <= -12839:
                return 't'
            if asc >= -12838 and asc <= -12557:
                return 'w'
            if asc >= -12556 and asc <= -11848:
                return 'x'
            if asc >= -11847 and asc <= -11056:
                return 'y'
            if asc >= -11055 and asc <= -10247:
                return 'z'
            return text

    @classmethod
    def alpha_text(cls, text):
        if cls.equal_ignore_case(text, None):
            return None
        lst = list(text.lower().strip().replace(' ', ''))
        char_list = []
        for each_text in lst:
            char_list.append(cls.__single_get_first(each_text))
        return ''.join(char_list)

    @classmethod
    def conversion_chinese_code(cls, str_text,
                                encode_type=CResource.Encoding_UTF8,
                                decode_type=CResource.Encoding_GBK) -> str:
        """
        转换中文编码
        :param str_text:
        :param encode_type:
        :param decode_type:
        :return:
        """
        str_text = cls.any_2_str(str_text) \
            .encode(encode_type, "surrogateescape") \
            .decode(decode_type)
        return str_text

    @classmethod
    def dict_append_dict(cls, dict_part1: dict, dict_part2: dict):
        if dict_part2 is not None:
            dict_part1.update(dict_part2)
        return dict_part1

    @classmethod
    def sql_split(cls, sql_text: str, seperator: str = ';') -> list:
        multi_sql_text = cls.any_2_str(sql_text)
        result = []
        list_row = multi_sql_text.split('\n')
        current_sql = ''
        for row in list_row:
            if not cls.any_2_str(row).endswith(seperator):
                current_sql = cls.str_append(current_sql, cls.any_2_str(row))
            else:
                current_sql = cls.str_append(current_sql, cls.any_2_str(row).rstrip(seperator))
                result.append(current_sql)
                current_sql = ''

        return result

    @classmethod
    def regular_str_escape_character_process(cls, regular_str: str) -> str:
        if CUtils.equal_ignore_case(regular_str, ''):
            return regular_str
        regular_str = regular_str.replace('(', r'\(').replace(')', r'\)') \
            .replace('+', r'\+').replace('^', r'\^').replace('.', r'\.')
        return regular_str

    @classmethod
    def split_of_regular(cls, regular: str, text, maxsplit=0, flags=0) -> list:
        if text is None:
            return []
        try:
            text_list = re.split(regular, text, maxsplit, flags)
        except:
            text_list = []
        return text_list

    @classmethod
    def findall_of_regular(cls, regular: str, text, flags=0) -> list:
        if text is None:
            return []
        try:
            text_list = re.findall(regular, text, flags)
        except:
            text_list = []
        return text_list

    @classmethod
    def findall_of_regular_first_value(cls, regular: str, text, flags=0):
        if text is None:
            return []
        try:
            text_list = re.findall(regular, text, flags)
        except:
            text_list = []
        if len(text_list) == 0:
            list_value = None
        elif type(text_list[0]) is tuple:
            for value in text_list[0]:
                if not CUtils.equal_ignore_case(value, ''):
                    list_value = value
        else:
            list_value = text_list[0]
        return list_value

    @classmethod
    def clear_quoter(cls, text: str) -> str:
        rt_text = cls.any_2_str(text)
        rt_text = rt_text.replace("'", '')
        rt_text = rt_text.replace('"', '')
        return rt_text

    @classmethod
    def list_item_by_id(cls, items: list, item_property_name, item_property_value) -> any:
        """
        找到符合要求的第一个item
        :param items:
        :param item_property_name:
        :param item_property_value:
        :return:
        """
        if items is None:
            return None

        for item in items:
            item_value = cls.dict_value_by_name(item, item_property_name, None)
            if item_value == item_property_value:
                return item
        else:
            return None

    @classmethod
    def list_item_by_index(cls, items: list, item_index: int, default_value) -> any:
        """
        找到符合要求的第一个item
        :param items:
        :param item_index: 索引
        :param default_value: 默认值
        :return:
        """
        if items is None:
            return default_value

        if item_index <= len(items):
            try:
                return items[item_index]
            except:
                return default_value
        else:
            return default_value

    @classmethod
    def list_item_list_by_id(cls, items: list, item_property_name, item_property_value) -> list:
        """
        找到符合要求的所有item
        :param items:
        :param item_property_name:
        :param item_property_value:
        :return:
        """
        if items is None:
            return []

        result = []
        for item in items:
            item_value = cls.dict_value_by_name(item, item_property_name, None)
            if item_value == item_property_value:
                result.append(item)

        return result

    @classmethod
    def dict_keys(cls, dict_obj: dict) -> list:
        if dict_obj is None:
            return []
        else:
            result = list()
            keys = dict_obj.keys()
            for key in keys:
                result.append(cls.any_2_str(key))
            return result

    @classmethod
    def iif(cls, exp, value, else_value):
        if exp is None:
            return else_value
        elif exp:
            return value
        else:
            return else_value

    @classmethod
    def any_2_list(cls, value):
        if value is None:
            return []
        elif not cls.is_list(value):
            return [value]
        else:
            return value

    @classmethod
    def dict_remove(cls, dict_obj: dict, dict_key: str, ignore_case=True):
        if dict_obj is None:
            return
        if CUtils.list_exists(
                CUtils.dict_keys(dict_obj),
                dict_key,
                ignore_case
        ):
            dict_obj.pop(dict_key)

    @classmethod
    def dict_same(cls, dict_obj1: dict, dict_obj2: dict) -> bool:
        return dict_obj1 == dict_obj2

    @classmethod
    def float_inf(cls, value):
        return float("inf") == value

    @classmethod
    def escape_arg(cls, value):
        result = '{}'.format(value)
        return parse.unquote(result)


if __name__ == '__main__':
    pass
