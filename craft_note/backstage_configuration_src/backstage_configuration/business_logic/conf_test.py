# -*- coding:utf-8 -*-
'''
@author: kexh
@update: 2017/11/02

'''
import json
import urlparse
from common.logger import logger
from backstage_configuration_config import *
from common.net.http_op import HttpOperation
from backstage_configuration.configure_constant import ConfigureConstant

class ConfTest(object):
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.servers_keys = []# just a normal value here and will change in val_input.
        self.ask = {}
        self.path = ""
        self.answer = ""

    def val_input(self):
        if self.data_dict == {} or ('q_sentence' not in self.data_dict):
            result = "未有q_sentence字段或q_sentence字段的值无法解析。"
            logger.info("未有q_sentence字段或q_sentence字段的值无法解析。")
            return result
        if 'apply_scene' not in self.data_dict:
            result = "未有apply_scene字段或apply_scene字段的值无法解析。"
            logger.info("未有apply_scene字段或apply_scene字段的值无法解析。")
            return result
        if int(self.data_dict['apply_scene']) not in [0, 1, 2]:
            result = "apply_scene字段的值error。"
            logger.info("apply_scene字段的值error。")
            return result
        if int(self.data_dict['apply_scene']) == 0:
            self.servers_keys = ["semantic_main_entrance"]
        elif int(self.data_dict['apply_scene']) == 1:
            self.servers_keys = ["semantic_wechat_entrance"]
        elif int(self.data_dict['apply_scene']) == 2:
            self.servers_keys = ["semantic_main_entrance", "semantic_wechat_entrance"]
        return True

    def http_r(self, servers_key, timeout=50):
        tag = True
        try:
            url = urlparse.urljoin('http://' + servers_dict[servers_key][0] + ':'
                                   + servers_dict[servers_key][1], self.path)
            logger.info("url in requests op: {}".format(url))
            print ("url in requests op: {}".format(url))
            ans = HttpOperation.post(url=url, data=json.dumps(self.ask), timeout=timeout).text
            # ans = '["sth", "sth too"]'
            logger.info("answer from http request: {}".format(ans))
            if ans[0] != "[" and ans[0] != "{":
                logger.warning("may error here: {}".format(ans))
                ans = "未知错误: " + str(ans)
                tag = False
        except Exception as e:
            logger.warning("error here: {}".format(e))
            ans = "未知错误: " + str(e)
            tag = False
        return tag, ans

    def val_output_jiqi(self, ans):
        dm_data = json.loads(ans)
        # print("type: {}. dm_data: {}".format(type(dm_data), dm_data))
        logger.info("type: {}. dm_data: {}".format(type(dm_data), dm_data))
        data = {}
        d_dict = dm_data[0]
        # print("dm_data[0]: {}".format(dm_data[0]))

        data['emotion_type'] = (d_dict.get('emotion', {})).get('fine-grained', '')
        data['emotion_target'] = (d_dict.get('emotion', {})).get('subject', '')
        m_intent_type = (d_dict.get('func', {})).get('type', '')
        # print m_intent_type
        cc = ConfigureConstant()
        if m_intent_type in cc.intent_type_map:
            data['m_intent_type'] = cc.intent_type_map[m_intent_type]
        else:
            data['m_intent_type'] = ''
        data['text'] = d_dict.get('text', '')
        # print("data text: {}".format(data['text']))
        logger.info("data text: {}".format(data['text']))
        # return_body = comb_json(data)
        return data#return_body

    def val_output_wechat(self, ans):
        dm_data = json.loads(ans)
        logger.info("type: {}. dm_data: {}".format(type(dm_data), dm_data))
        # wechat's return has not [m_intent_type, emotion_type, emotion_target]'s value.
        data = dict(emotion_type = '', emotion_target = '', m_intent_type = '')
        d_dict = dm_data
        data['text'] = d_dict.get('respData', {}).get('reply', '')
        logger.info("data text: {}".format(data['text']))
        return data#return_body
		
def main(data_dict):
    ct = ConfTest(data_dict)
    val_result = ct.val_input()
    if val_result == True:
        # 如请求“通用”服，暂时先返回一条结果。后面如果data改列表结果，会加多一个"apply_scene"字段。前端也需要改。
        # 这个地方后面改成循环
        servers_key = ct.servers_keys[0]
        if servers_key == "semantic_wechat_entrance":
            ct.ask = {...
                    }
            ct.path = fragments["test"][1]
        else:
            ct.ask = {...}
            ct.path = fragments["test"][0]
        req_tag, ans = ct.http_r(servers_key)
        if req_tag == True:
            if servers_key == "semantic_wechat_entrance":
                result = ct.val_output_wechat(ans)
            else:
                result = ct.val_output_jiqi(ans)
            return result
        else:
            return "测试语义结果时，语义主服务semantic_main_entrance or semantic_wechat_entrance未响应。"
    else:
        return val_result

if __name__ == "__main__":
    data_dict = {
        "q_sentence": "我相信你",
        "apply_scene": 2
    }
    print main(data_dict)["text"]
