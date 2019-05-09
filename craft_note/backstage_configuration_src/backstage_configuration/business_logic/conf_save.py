# -*- coding:utf-8 -*-
'''
@author: kexh
@update: 2017/11/02

'''
import json
import urlparse
from common.logger import logger
import backstage_configuration_config as pc
from backstage_configuration_config import *
from common.net.http_op import HttpOperation
from backstage_configuration.configure_constant import ConfigureConstant
from backstage_configuration.configure_constant import check_value
from backstage_configuration.storage.business_storage_op import StorageOperation
'''
1. local_id， so_temp, bg_id_server等变量是原来为多服务器各种同步逻辑而设计的，为避免后面需求又改回旧的，先保留。
2. 保存更新到bg_conf server：
    同一个句子如果再次编辑其答句or泛化语句：a_sentence_list和para_sentence_list的各个元素均会被更新（也就是，删detail表相关条目后，再插入新条目）。
3. 假如base表插入成功，但是detail表插入失败，base表的相关条目不会被删了，因为有可能是update操作
'''

class ConfSave(object):
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.tag = pc.servers_db.get(data_dict.get("target_server", ""), 0)
        self.so = StorageOperation(tag = self.tag)
        self.local_id = self.check_local_id()# local table_main

    def val_input(self):
        if self.data_dict == {} or ('q_sentence' not in self.data_dict):
            result = "未传入q_sentence的值"
            logger.info("未传入q_sentence的值")
            return result
        cc = ConfigureConstant()
        if self.data_dict.get('m_intent_type', '') == '' or self.data_dict['m_intent_type'] in cc.intent_list:
            value_leg = check_value(emotion_type=self.data_dict.get('emotion_type', ''),
                                    emotion_target=self.data_dict.get('emotion_target', ''),
                                    emotion_polar=self.data_dict.get('emotion_polar', '')
                                    )
        else:
            value_leg = False
        if value_leg == False:
            return "m_intent_type, emotion_type, emotion_target或emotion_polar中存在不合法的值。"
        return True

    def check_local_id(self):
        self.so.set_table(pc.table_base[0])
        local_id = int(self.data_dict.get("bg_id", 0))
        if local_id == 0:
            q_sentence = str(self.data_dict.get("q_sentence", ""))
            check_result = self.so.select_limit(('q_sentence', q_sentence))
            if isinstance(check_result, tuple) and len(check_result) > 0:
                local_id = check_result[0][0]
                logger.info("local_id: {}".format(local_id))
                # print ("local_id: {}".format(local_id))
        return local_id

    def q_sentence_insert(self, so_temp):
        '''
        适用场景：
            1. 保存更新到bg_conf server的功能中，insert bg_conf server主表的情况
        '''
        so_temp.set_table(pc.table_base[0])
        kw = dict(
            q_sentence=str(self.data_dict.get("q_sentence", "")),
            emotion_type=str(self.data_dict.get("emotion_type", "")),
            emotion_target=str(self.data_dict.get("emotion_target", "")),
            emotion_polar=str(self.data_dict.get("emotion_polar", "")),
            m_intent_type=str(self.data_dict.get("m_intent_type", "")),
            q_sentence_priority=str(self.data_dict.get("q_sentence_priority", ""))
        )
        kw.update(dict(sync_status=int("10000000")))
        bg_id_server = so_temp.insert_sql(**kw)
        self.local_id = bg_id_server
        return bg_id_server

    def q_sentence_update(self, so_temp, bg_id_server):
        '''
        适用场景：
            1. 保存更新到bg_conf server的功能中，bg conf server中主表已经存在的情况
        '''
        so_temp.set_table(pc.table_base[0])
        kw = dict(
            bg_id=bg_id_server,
            q_sentence=str(self.data_dict.get("q_sentence", "")),
            emotion_type=str(self.data_dict.get("emotion_type", "")),
            emotion_target=str(self.data_dict.get("emotion_target", "")),
            emotion_polar=str(self.data_dict.get("emotion_polar", "")),
            m_intent_type=str(self.data_dict.get("m_intent_type", "")),
            q_sentence_priority=str(self.data_dict.get("q_sentence_priority", ""))
        )
        if self.tag != 0:
            kw.update(dict(save_time=None))
        line_count = so_temp.update_sql(**kw)
        return line_count

    def a_sentence_insert(self, so_temp, bg_id_server):
        '''
        适用场景：保存更新到bg_conf server的功能中，insert bg_conf server的detail表的情况
        '''
        so_temp.set_table(pc.table_base[1])
        a_sentence_list = self.data_dict.get("a_sentence_list", [])
        so_temp.delete_sql(**dict(bg_id=bg_id_server))
        for a_sentence_dict in a_sentence_list:
            kw = dict(
                bg_id=bg_id_server,
                a_sentence = str(a_sentence_dict.get("a_sentence", "")),
                favor_num = float(a_sentence_dict.get("favor_num", 0)),
                mood_num = float(a_sentence_dict.get("mood_num", 0)),
                apply_scene = int(a_sentence_dict.get("apply_scene", 0))
            )
            so_temp.insert_sql(**kw)

    def para_sentence_insert(self, so_temp, bg_id_server):
        '''
        适用场景：
            1. 保存更新到bg_conf server的功能中，insert bg_conf server的detail表的情况
        '''
        so_temp.set_table(pc.table_base[2])
        para_sentence_list = self.data_dict.get("para_sentence_list", [])
        so_temp.delete_sql(**dict(bg_id=bg_id_server))
        for para_sentence_dict in para_sentence_list:
            kw = dict(
                bg_id=bg_id_server,
                para_sentence = str(para_sentence_dict.get("para_sentence", "")),
                enable = int(para_sentence_dict.get("enable", 0)),
                score = float(para_sentence_dict.get("score", 0))
            )
            so_temp.insert_sql(**kw)

    def es_sync_status(self):
        self.so.set_table(pc.table_base[0])
        check_result = self.so.select_limit(('id', int(self.local_id)))
        columns = pc.columns_common[pc.table_base[0]] + ["sync_status"]
        data_main = dict(zip(columns, list(check_result[0])))
        es_input = self.data_dict
        es_input["bg_id"] = int(self.local_id)
        es_input["q_sentence"] = str(data_main["q_sentence"])# if data_main["q_sentence"] != None else ""
        es_input["emotion_type"] = str(data_main["emotion_type"]) if data_main["emotion_type"] != None else ""
        es_input["emotion_target"] = str(data_main["emotion_target"]) if data_main["emotion_target"] != None else ""
        es_input["emotion_polar"] = str(data_main["emotion_polar"]) if data_main["emotion_polar"] != None else ""
        es_input["m_intent_type"] = str(data_main["m_intent_type"]) if data_main["m_intent_type"] != None else ""
        es_input["q_sentence_priority"] = str(data_main["q_sentence_priority"]) if data_main["q_sentence_priority"] != None else ""
        sync_status = "10000000" if data_main["sync_status"] in [None, ""] else str(data_main["sync_status"])

        a_sentence_list = self.data_dict.get("a_sentence_list", [])
        a_sentence_list_0 = []
        a_sentence_list_1 = []
        for a_sentence_dict in a_sentence_list:
            apply_scene = int(a_sentence_dict.get("apply_scene", 0))
            if apply_scene == 0 or apply_scene == 2:
                a_sentence_list_0.append(a_sentence_dict)
            elif apply_scene ==1 or apply_scene ==2:
                a_sentence_list_1.append(a_sentence_dict)
            else:
                logger.info("unkown a_sentence_dict here: {}".format(a_sentence_dict))
        # 没有机器服答句的话，不会存其他属性到机器服，不然影响sync_status的值。
        ans_all = ""
        if a_sentence_list_0 != []:
            es_input_0 = es_input
            es_input_0["a_sentence_list"] = a_sentence_list_0
            ans_0, sync_status = self.link_to_es(es_input_0, sync_status = sync_status, k = 0)
            logger.info("len of a_sentence_list_0: {}".format(len(a_sentence_list_0)))
            ans_all = ans_all + ans_0
        if a_sentence_list_1 != []:
            es_input_1 = es_input
            es_input_1["a_sentence_list"] = a_sentence_list_1
            ans_1, sync_status = self.link_to_es(es_input_1, sync_status = sync_status, k = 1)
            logger.info("len of a_sentence_list_1: {}".format(len(a_sentence_list_1)))
            ans_all = ans_all + ans_1
        self.so.set_table(pc.table_base[0])
        kw = dict(
            bg_id=self.local_id,
            sync_status=int(sync_status)
        )
        self.so.update_sql(**kw)
        if ans_all == "":
            return True
        else:
            return "未能同步到所有语义服务器的ES中，但已保存到后台配置中心：" + ans_all
			
    def link_to_es(self, save_data, sync_status, k):
        '''
        usage: link to es and reset sync status
        '''
        ans_all = ""
        if k == 0:
            ans = self.http_r("semantic_main_entrance", save_data)
            if ans == "":
                sync_status = sync_status[:1] + "1" + sync_status[2:]
            else:
                ans_all = ans_all + " semantic_main_entrance return: " + ans
        elif k == 1:
            ans = self.http_r("semantic_wechat_entrance", save_data)
            if ans == "":
                sync_status = sync_status[:2] + "1" + sync_status[3:]
            else:
                ans_all = ans_all + " semantic_wechat_entrance return: " + ans
        return ans_all, sync_status

    def http_r(self, servers_key, save_data, timeout=10):
        '''
        sth of es post:
            es_save = EsSave(save_data)
            if es_save.val_input() == True:
                ans = es_save.save_to_es()
                ans = json.dumps(ans)
            else:
                ans = dict(code=02, es_result='es_result')
        '''
        try:
            url = urlparse.urljoin('http://' + servers_dict[servers_key][0] + ':'
                                   + servers_dict[servers_key][1], fragments["save"])
            logger.info("url in this save op: {}".format(url))
            # ans = HttpRequestClient().post(url, save_data, timeout=timeout)
            ans = HttpOperation.post(url, json.dumps(save_data), timeout=timeout).text
            logger.info("answer from save request: {}".format(ans))
            ans_dict = json.loads(ans)
            if ans_dict["code"] != 10:
                logger.warning("may save to es fail here: {}".format(ans))
                ans = "未知错误: " + str(ans)
            else:
                ans = ""
        except Exception as e:
            logger.warning("error here: {}".format(e))
            ans = "未知错误: " + str(e)
        return ans		

def main(data_dict):
    cs = ConfSave(data_dict)
    val_result = cs.val_input()
    if isinstance(val_result, str):
        logger.warning("error when val input: {}".format(val_result))
        return val_result
    if cs.local_id == 0:
        bg_id_server = cs.q_sentence_insert(cs.so)
        logger.info("insert table_main and local_id is {}".format(cs.local_id))
    else:
        bg_id_server = cs.local_id
        cs.q_sentence_update(cs.so, cs.local_id)
        logger.info("update table_main in local and will insert detail tables.")
    cs.a_sentence_insert(cs.so, bg_id_server)
    cs.para_sentence_insert(cs.so, bg_id_server)
    sync_result = cs.es_sync_status()
    if isinstance(sync_result, str):
        return sync_result
    logger.info("bg_id in bg_conf_center after conf save: {}".format(cs.local_id))
    return dict(bg_id = int(cs.local_id))
