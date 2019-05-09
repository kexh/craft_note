# -*- coding:utf-8 -*-
'''
@author: kexh
@update: 2017/09/28

目前只有"bg_conf_server"提供了这部分的功能。
'''

from backstage_configuration.storage.business_storage_op import StorageOperation

import backstage_configuration_config as pc
from common.logger import logger


class ConfDetail(object):
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.tag = pc.servers_db.get(data_dict.get("target_server", ""), 0)
        self.so = StorageOperation(tag = self.tag)
        self.data = dict(
                        bg_id = None,
                        q_sentence = "",
                        para_sentence_list = [],
                        a_sentence_list = [],
                        emotion_type = "",
                        emotion_target = "",
                        emotion_polar = "",
                        m_intent_type = "",
                        save_time = "",
                        sync_status = 0,
                        q_sentence_priority = ""
                    )

    def val_input(self):
        if self.data_dict == {} or ('bg_id' not in self.data_dict and 'q_sentence' not in self.data_dict):
            result = "未传入bg_id或q_sentence的值"
            logger.info("未传入bg_id或q_sentence的值")
            return result
        return True

    def q_sentence_op(self):
        self.so.set_table(pc.table_base[0])
        if 'bg_id' in self.data_dict:
            result_base = self.so.select_limit(('id', int(self.data_dict['bg_id'])))
        else:
            result_base = self.so.select_limit(('q_sentence', self.data_dict.get('q_sentence', '')))
        if isinstance(result_base, str):
            logger.warning("sth error here: {}".format(result_base))
            return result_base
        values = list(result_base[0])
        if values == []:
            return "查询结果为空"
        columns = pc.columns_common[pc.table_base[0]]
        columns = columns + ["sync_status"] if int(self.tag)==0 else columns + ["local_id"]
        data_new = dict(zip(columns, values))
        self.data["bg_id"] = int(data_new["id"])
        self.data["save_time"] = str(data_new["save_time"])
        if data_new["q_sentence"] != None: self.data["q_sentence"] = str(data_new["q_sentence"])
        if data_new["emotion_type"] != None: self.data["emotion_type"] = str(data_new["emotion_type"])
        if data_new["emotion_target"] != None: self.data["emotion_target"] = str(data_new["emotion_target"])
        if data_new["emotion_polar"] != None: self.data["emotion_polar"] = str(data_new["emotion_polar"])
        if data_new["m_intent_type"] != None: self.data["m_intent_type"] = str(data_new["m_intent_type"])
        if data_new["q_sentence_priority"] != None: self.data["q_sentence_priority"] = str(data_new["q_sentence_priority"])
        if data_new["sync_status"] != None: self.data["sync_status"] = int(data_new["sync_status"])
        # 前端不再需要输出sync_status字段
        self.data.pop("sync_status") if self.data.has_key("sync_status") else self.data
        return True

    def a_sentence_op(self):
        self.so.set_table(pc.table_base[1])
        result_list = self.so.select_limit(("bg_id", self.data["bg_id"]))
        if isinstance(result_list, str):
            logger("sth error her: {}".format(result_list))
        for values in result_list:
            result_a_sentence = dict()
            columns = pc.columns_common[pc.table_base[1]]
            data_line = dict(zip(columns, values))
            result_a_sentence["a_sentence_id"] = int(data_line["id"])
            result_a_sentence["save_time_a_sentence"] = str(data_line["save_time"])
            result_a_sentence["a_sentence"] = str(data_line["a_sentence"]) if data_line["a_sentence"] != None else ""
            result_a_sentence["favor_num"] = float(data_line["favor_num"]) if data_line["a_sentence"] != None else 0
            result_a_sentence["mood_num"] = float(data_line["mood_num"]) if data_line["a_sentence"] != None else 0
            result_a_sentence["apply_scene"] = int(data_line["apply_scene"]) if data_line["a_sentence"] != None else 0
            self.data["a_sentence_list"].append(result_a_sentence)

    def para_sentence_op(self):
        self.so.set_table(pc.table_base[2])
        result_list = self.so.select_limit(('bg_id', self.data["bg_id"]))
        if isinstance(result_list, str):
            logger("sth error her: {}".format(result_list))
        for values in result_list:
            result_para_sentence = dict()
            columns = pc.columns_common[pc.table_base[2]]
            data_line = dict(zip(columns, values))
            result_para_sentence["para_sentence"] = str(data_line["para_sentence"]) if data_line["para_sentence"] != None else ""
            result_para_sentence["enable"] = int(data_line["enable"]) if data_line["enable"] != None else 0
            result_para_sentence["score"] = float(data_line["score"]) if data_line["score"] != None else 0
            self.data["para_sentence_list"].append(result_para_sentence)

def main(data_dict):
    conf_detail = ConfDetail(data_dict)
    val_result = conf_detail.val_input()
    if isinstance(val_result, str):
        return val_result
    exist_result = conf_detail.q_sentence_op()
    if isinstance(exist_result, str):
        return exist_result
    conf_detail.a_sentence_op()
    conf_detail.para_sentence_op()
    logger.info("conf detail data: {}".format(conf_detail.data))
    return conf_detail.data
