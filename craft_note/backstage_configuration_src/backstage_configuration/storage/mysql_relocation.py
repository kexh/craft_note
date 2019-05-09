# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/02
'''
import time
import json
import requests
from common.logger import logger
import backstage_configuration_config as pc
from backstage_configuration.storage.business_storage_op import StorageOperation

url = "..."
# 每个表申请自己的游标，避免混乱
so_q = StorageOperation(0)
so_a = StorageOperation(0)
so_para = StorageOperation(0)

def query_comb(i):
    q_sentence_fetchone = so_q.cursor.fetchone()
    # if i < 10:
    #     return None, None, None
    # print i
    logger.info("go to index: {}".format(i))
    bg_id = q_sentence_fetchone[0]
    logger.info("bg_id: {}".format(bg_id))
    columns = pc.columns_common[pc.table_base[0]] + ["sync_status"]
    q_sentence_dict = dict(zip(columns, q_sentence_fetchone))
    query_sentence = q_sentence_dict["q_sentence"]
    # todo
    # print q_sentence_dict
    intent = dict(
        emotion_type = q_sentence_dict["emotion_type"] if q_sentence_dict["emotion_type"] != None else u"",
        emotion_target = q_sentence_dict["emotion_target"] if q_sentence_dict["emotion_target"] != None else u"",
        emotion_polar = q_sentence_dict["emotion_polar"] if q_sentence_dict["emotion_polar"] != None else u"",
        m_intent_type = 1,
        q_sentence_priority = q_sentence_dict["q_sentence_priority"] if q_sentence_dict["q_sentence_priority"] != None else u"",
    )
    return bg_id, query_sentence, intent

def answer_comb(bg_id):
    select_str_a = "SELECT * FROM amber_conf_a_sentence WHERE bg_id = " + str(bg_id)
    try:
        so_a.cursor.execute(select_str_a)
        result_list = so_a.cursor.fetchall()
    except Exception as e:
        logger.info("error (bg_id: {})when get a_sentence: {}".format(bg_id, str(e)))
        result_list = []
    a_sentence_list = []
    for values in result_list:
        columns = pc.columns_common[pc.table_base[1]]
        data_line = dict(zip(columns, values))
        a_sentence_dict = dict(
            answer_template = data_line["a_sentence"] if data_line["a_sentence"] != None else u"",
            hupo_softspot = float(data_line["favor_num"]) if data_line["a_sentence"] != None else 0,
            hupo_emotion = float(data_line["mood_num"]) if data_line["a_sentence"] != None else 0,
            apply_scene = int(data_line["apply_scene"]) if data_line["a_sentence"] != None else 0
        )
        a_sentence_list.append(a_sentence_dict)
    return a_sentence_list

def para_comb(bg_id):
    select_str_para = "SELECT * FROM amber_conf_para_sentence WHERE bg_id = " + str(bg_id)
    try:
        so_para.cursor.execute(select_str_para)
        result_list = so_para.cursor.fetchall()
    except Exception as e:
        logger.info("error (bg_id: {})when get para_sentence: {}".format(bg_id, str(e)))
        result_list = []
    para_sentence_list = []
    for values in result_list:
        columns = pc.columns_common[pc.table_base[2]]
        data_line = dict(zip(columns, values))
        para_sentence_dict = dict(
            para_sentence = data_line["para_sentence"] if data_line["para_sentence"] != None else u"",
            enable = int(data_line["enable"]) if data_line["enable"] != None else 0,
            score = float(data_line["score"]) if data_line["score"] != None else 0
        )
        para_sentence_list.append(para_sentence_dict)
    return para_sentence_list

def req_config_corpus(bg_id, req_dict):
    resp_tag = False
    try:
        resp = requests.post(url=url, data=json.dumps(req_dict))
        if int(json.loads(resp.text)["code"]) == 2000:
            logger.info("{}: {}".format(str(bg_id), "success"))
            resp_tag = True
    except Exception as e:
        logger.info("error (bg: {}) when push to config corpus: {}".format(str(bg_id), e))
    return resp_tag

if __name__ == "__main__":
    so_q.cursor.execute("select count(*) from amber_conf_q_sentence")
    count = so_q.cursor.fetchall()[0][0]
    select_str_q = "SELECT * FROM amber_conf_q_sentence"
    so_q.cursor.execute(select_str_q)
    logger.info("count: {}".format(count))
    for i in range(count):
        bg_id, query_sentence, intent = query_comb(i)
        if (bg_id, query_sentence, intent) == (None, None, None):
            continue
        answer_list = answer_comb(bg_id)
        generalization = para_comb(bg_id)
        query_seg = dict(bg_id=0, query_sentence=query_sentence, generalization=generalization)
        req_dict = dict(query_list=[query_seg], intent=intent, answer_list=answer_list)
        resp_tag = req_config_corpus(bg_id, req_dict)
        if resp_tag!=True:
            print "unsuccess: {}".format(bg_id)
        else:
            print "success"
        time.sleep(4)



