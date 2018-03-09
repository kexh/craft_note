# -*- coding:utf-8 -*-
'''
@author: kexh
@update: 2017/09/28

目前只有"bg_conf_server"提供了这部分的功能。
'''

from backstage_configuration.storage.business_storage_op import StorageOperation

import backstage_configuration_config as pc
from common.logger import logger


class ConfList(object):
    def __init__(self, data_dict):
        self.data_dict = data_dict
        # 由于产品决定只保存至正式服和读取正式服列表，所以tag默认值为2
        self.tag = 2#pc.servers_db.get(data_dict.get("target_", ""), 2)
        self.so = StorageOperation(tag = self.tag)
        self.data = dict(total=0, select_result=[])

    def val_input(self):
        if self.data_dict == {} or ('limit_count' and 'backward_time' not in self.data_dict):
            result = "未传入limit_count或backward_time的值"
            logger.info("未传入limit_count或backward_time的值")
            return result
        return True

    def select_setting(self):
        '''
        m_intent_type目前不接收值，不传给self.sc.select_sql
        :param kw: column_name0=column_value0, column_name1=column_value1
        '''
        select_dict = {}
        if self.data_dict.get('limit_count', 0)!=0:
            # limit_count为0，视同limit_count不存在
            select_dict['limit_count'] = self.data_dict['limit_count']
        if self.data_dict.get('backward_time', '')!='':
            # backward_time为""，视同backward_time不存在
            select_dict['backward_time'] = self.data_dict['backward_time']
        if int(self.data_dict.get('page_no', 1)):
            # 如果没有page_no或其值为空，默认返回第一页内容
            select_dict['limit_page'] = str(pc.page_limit * (int(self.data_dict.get('page_no', 1))-1)) + "," + str(pc.page_limit)
        return select_dict

    def q_sentence_op(self):
        self.so.set_table(pc.table_base[0])
        select_dict = self.select_setting()
        result_list = self.so.select_limits(select_dict)
        if isinstance(result_list, str):
            return result_list
        data = []
        for values in result_list:
            result_q_sentence = dict()
            columns = pc.columns_common[pc.table_base[0]]
            columns = columns + ["sync_status"] if int(self.tag) == 0 else columns + ["local_id"]
            data_line = dict(zip(columns, values))
            result_q_sentence["bg_id"] = int(data_line["id"])
            result_q_sentence["a_sentence_count"] = self.a_sentence_op(int(data_line["id"]))
            result_q_sentence["save_time"] = str(data_line["save_time"])
            result_q_sentence["q_sentence"] = str(data_line["q_sentence"]) if data_line["q_sentence"] != None else ""
            # result_q_sentence["sync_status"] = int(data_line["sync_status"]) if data_line["sync_status"] != None else 0
            self.data["select_result"].append(result_q_sentence)
        select_origin = "select count(*) from " + pc.table_main
        self.data["total"] = int(self.so.select_limit(None, select_origin)[0][0])
        return data

    def a_sentence_op(self, bg_id):
        self.so.set_table(pc.table_base[1])
        select_origin = "select count(*) from " + pc.table_base[1] + " where bg_id = " + str(bg_id)
        a_sentence_count = int(self.so.select_limit(None, select_origin)[0][0])
        return a_sentence_count


def main(data_dict):
    conf_list = ConfList(data_dict)
    val_result = conf_list.val_input()
    if isinstance(val_result, str):
        return val_result
    conf_list.q_sentence_op()
    return conf_list.data

