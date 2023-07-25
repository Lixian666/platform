import requests

from base.c_resource import CResource
from base.c_utils import CUtils


class CHttp(CResource):
    @classmethod
    def get(cls, url, option=None):
        headers = CUtils.dict_value_by_name(option, cls.Name_Headers, None)
        data = CUtils.dict_value_by_name(option, cls.Name_Data, None)
        stream = CUtils.dict_value_by_name(option, cls.Name_Stream, None)
        timeout = CUtils.dict_value_by_name(option, cls.Name_Timeout, 60)
        params = CUtils.dict_value_by_name(option, cls.NAME_Params, 60)

        req = requests.get(url, headers=headers, data=data, params=params, stream=stream, timeout=timeout)
        return req

    @classmethod
    def get_content(cls, url, option=None):
        return cls.get(url, option).json()

    @classmethod
    def get_html_text(cls, url, option=None):
        return cls.get(url, option).text

    @classmethod
    def open(cls, url, option=None):
        headers = CUtils.dict_value_by_name(option, cls.Name_Headers, None)
        data = CUtils.dict_value_by_name(option, cls.Name_Data, None)
        json = CUtils.dict_value_by_name(option, cls.Name_Json, None)
        files = CUtils.dict_value_by_name(option, cls.Name_Files, None)
        timeout = CUtils.dict_value_by_name(option, cls.Name_Timeout, 60)
        req = requests.post(url, headers=headers, data=data, json=json, files=files, timeout=timeout)
        return req

    @classmethod
    def post(cls, url, option=None):
        return cls.open(url, option).json()

    @classmethod
    def close(cls, req):
        req.close()


if __name__ == "__main__":
    test_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=0428561e-6188-4977-9e5d-21057339df13'
    test_header = {"Content-Type": "application/json"}
    test_data_test = {
        "msgtype": "text",
        "text": {
            "content": "chttp类单部@人测试",
            "mentioned_mobile_list": ["18437918096", "@all"]
        }
    }
    option_test = {
        'hesders': test_header,
        'json': test_data_test
    }

    print(CHttp.post(test_url, option_test))
