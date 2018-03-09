# -*- coding:utf-8 -*-
'''
@author: kexh
@update: 2017/09/28
'''

import importlib
import json

from backstage_configuration_config import scripts_dict


def comb_json(data):
    # todo: 后面还是要改成可以传code_description进来
    if isinstance(data, str):
        return dict(code=2100, code_description=data, data={})
    elif data == []:
        return dict(code=4000, code_description="请求失败", data={})
    elif data == {}:# or result.has_key('id') == False:
        return dict(code=4000, code_description="请求失败", data={})
    request_body = dict()
    request_body["code"] = 2000
    request_body["code_description"] = "请求成功"
    request_body["data"] = data
    # json.dumps(return_body, ensure_ascii=False,sort_keys=True)
    return request_body


def scripts_api(target_server, path, data):
    data_dict = json.loads(data)
    if path in scripts_dict.keys():
        api_module = importlib.import_module("backstage_configuration.business_logic." + scripts_dict[path])
    else:
        return_body = {
                "code": 4000,
                "code_description": "未知错误: " + "目前暂不支持该服务器或该接口服务的请求。",
                "data": {}
            }
        return return_body
    try:
        data = api_module.main(data_dict)
        return_body = comb_json(data)
    except Exception as e:
        return_body = {
                "code": 2100,
                "code_description": "未知错误: " + str(e),
                "data": {}
        }
    return return_body
