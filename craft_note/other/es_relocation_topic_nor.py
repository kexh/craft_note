# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2017/12/28
'''
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os, os.path
import json
import datetime
import operator
import numpy as np
from scipy import dot, linalg
from common.logger import logger
from common.db.es_op import EsClient
'''
es库数据搬迁；一个句子需只有一个topic_id（查旧es库验证），如果一个句子有多个topic_id，对其所有同topic_id的句子进行sv计算并比较得分，得到最接近的topic_id，然后存库。
0. 建index的脚本跑两次，一次正式用的，一次测试用的。
1. es_get 一次拿500条的topic_str和topic_id, 做es_check处理
2. es_save 一次保存一条数据，需要根据topic_str和topic_id拿到完整的数据，之后再存入新库

        判断当前处理对象其句子是否有多个topic_id...
        避免同一个句子多次计算最佳topic_id：
        1. 每次拿句子查在str_exist_list中是否存在，有就跳过，没有且在旧库有多个topic_id就计算，然后句子和最佳topic_id存库，且句子、(句子, topic_id)各自append到str_exist_list和match_list；
        * 为了避免程序报错导致str_exist_list和topic_id_match_list缓存丢失，句子和最佳topic_id要实时追加写入文件。
        但这种有个问题，如果旧库数据更新，最佳topic_id没有重新计算。能够满足时效性，但计算量增加的（此处应用场景旧库无数据增加，不做考虑）：
        每次拿到句子计算最佳topic_id，如果跟当前topic_id不一样就跳过，否则等到topic_id跟其实时计算得到的最佳topic_id一样时再存库。

{
	u'_score': 1.0,
	u'_type': u'feature_chat_dev_topic_type2',
	u'_id': u'AWA2BwnfLbOUX0luPyJh',
	u'_source': {
		u'topic_seven_w': u'non_q_statement',
		u'topic_normalized_1': u'nor_aa02b0nor_da25b0',
		u'topic_normalized_2': u'aa02b0<-nsubj<-da25b0',
		u'topic_pos': {
			u'comb': u'我们_PN反应_VV',
			u'value': u'PNVV',
			u'pos_index': u'我们反应'
		},
		u'topic_syntactical': u'我们<-nsubj<-反应',
		u'@timestamp': u'2017-12-08T20: 08: 39.000+0800',
		u'topic_sv': [
			...
		],
		u'topic_ner_string': u'',
		u'topic_svs': u'...',
		u'topic_ner': [],
		u'topic_id': u'85d24f42dc1011e78ee4509a4c09f6d1',
		u'topic_seg': u'我们反应呢',
		u'topic_str': u'我们反应呢'
	},
	u'_index': u'feature_chat_dev_topic_index2'
}

'''

es_ip = '172.26.1.33'
es_port = 9200
es_index = "feature_chat_dev_topic_index2"
doc_type = "feature_chat_dev_topic_type2"
es_index_2 = "feature_chat_dev_topic_index_201802"
doc_type_2 = "feature_chat_dev_topic_type_201802"



file_path = os.path.join(os.path.dirname(os.getcwd()), "data/log/")
time_tag = datetime.datetime.now().strftime('%m-%d_%H-%M-%S')
file_str_exist = file_path + time_tag + '_exist.txt'
file_match = file_path + time_tag + '_match.txt'
file_irreg = file_path + time_tag + '_irreg.txt'

size = 500

def es_get(from_int, size):
    '''
    列表元素格式如下：
    {
	u'_score': 1.0,
	u'_type': u'feature_chat_dev_topic_type2',
	u'_id': u'AWA2Ava1LbOUX0luPxgx',
	u'_source': {
		u'topic_str': u'睡觉吧我要是有事去了',
		u'topic_id': u'e6248a23dc0f11e78ee4509a4c09f6d1'
	    },
	u'_index': u'feature_chat_dev_topic_index2'
    }
    '''
    search_dict = {
	    "_source": ["topic_id", "topic_str"],
        "from": from_int,
        "size": size
    }
    result_list = EsClient(es_ip, es_port).search(es_index, doc_type, search_dict)
    # result_list = json.loads(result_list)
    return result_list

def es_topic_id_more(r_topic_str):
    # usage: 未存储的需要到旧库查是否有多个topic_id
    topic_id_list = []
    # 用这种方法搜索，不够精确匹配，比如搜“你好吗”，则“你好吗你好吗”也会出来。需要再做下过滤
    # bool + should ?
    search_dict = {
	"_source": ["topic_id", "topic_str"],
	"query": {
		"match_phrase": {
					"topic_str": r_topic_str
				}
        }
    }
    try:
        result_list = EsClient(es_ip, es_port).search(es_index, doc_type, search_dict)
    except Exception as e:
        logger.info("error when es_topic_id_more: {}".format(e))
        result_list = []
    for rr in result_list:
        rr_topic_id = rr.get('_source', {}).get('topic_id', '')
        rr_topic_str = rr.get('_source', {}).get('topic_str', '')
        if rr_topic_str == r_topic_str:
            topic_id_list.append(rr_topic_id)
    return topic_id_list

def es_topic_id_sv(topic_id_list, r_topic_str):
    should = []
    for i in topic_id_list:
        should.append({"match_phrase": {"topic_id": i}})
    # 放到一起请求，缩短时间
    search_dict = {
    "query": {
        "bool": {
            "should": should
            }
        }
    }
    try:
        result_list = EsClient(es_ip, es_port).search(es_index, doc_type, search_dict)
    except:
        result_list = []

    # 提取数据 [topic_sv_list_temp] "id_1": [(str_1_a, sv_1_a), (str_1_b, sv_1_b)]
    topic_dict = dict.fromkeys(topic_id_list, [])
    r_topic_sv = np.array([])
    for rr in result_list:
        rr_topic_id = rr.get('_source', {}).get('topic_id', '')
        if rr_topic_id not in topic_id_list:
            logger.info("111error! error! error!")
            continue
        rr_topic_str = rr.get('_source', {}).get('topic_str', '')
        rr_topic_sv = np.array(rr.get('_source', {}).get('topic_sv', []))
        topic_sv_list_temp = topic_dict[rr_topic_id]
        topic_sv_list_temp.append((rr_topic_str, rr_topic_sv))
        topic_dict.update({rr_topic_id: topic_sv_list_temp})
        if r_topic_str == rr_topic_str:
            r_topic_sv = rr_topic_sv
    if len(r_topic_sv)==0:
        logger.info("error: some sv is empty or not r_topic_str == rr_topic_str here.")
    return topic_dict, r_topic_sv

def topic_nor(topic_id_list, r_topic_str):
    topic_dict, r_topic_sv = es_topic_id_sv(topic_id_list, r_topic_str)
    if topic_dict == dict.fromkeys(topic_id_list, []):
        return ""
    topic_avg_dict = dict()
    for topic_id in topic_dict:
        # 针对每个topic，拿str对应的sv均作打分计算，除以个数（把str为原句的排除在外），得到该topic的平均分（todo：后面换成其他衡量方式）。
        topic_sv_list_temp = topic_dict[topic_id]
        sv_score = float(0)

        num = len(topic_sv_list_temp)
        for i, str_sv in enumerate(topic_sv_list_temp):
            if r_topic_str == str_sv[0]:
                num = num - 1
                logger.info("same!!!!")
                continue

            topic_sv_i = str_sv[1]
            try:
                sv_score_i = dot(r_topic_sv, topic_sv_i) / (linalg.norm(r_topic_sv) * linalg.norm(topic_sv_i))
                sv_score = sv_score + float(sv_score_i)
            except Exception as e:
                logger.info("error in topic_nor: "+str(e))
                num = num - 1
        if num == 0:
            topic_n_score_avg = 0.6 # 经常是集合里头只有原句一条
        else:
            topic_n_score_avg = float(sv_score) / float(num)
        topic_avg_dict[topic_id] = topic_n_score_avg

    sorted_avgs_dict = sorted(topic_avg_dict.items(), key=operator.itemgetter(1))
    topic_id = sorted_avgs_dict[0][0]
    logger.info("will return topic_id: {}".format(topic_id))
    return topic_id

def es_save(topic_str, topic_id):
    # 根据topic_str和topic_id拿到完整的数据，之后再存入新库
    search_dict = {
	"query": {
		"bool": {
			"must": [
				{
					"match_phrase": {
						"topic_str": topic_str
					}
				},
					{"match_phrase": {
						"topic_id": topic_id
                        }
                    }
                ]
            }
        }
    }
    try:
        result_list = EsClient(es_ip, es_port).search(es_index, doc_type, search_dict)
    except Exception as e:
        logger.info("error when es save get thing: {}".format(e))
        result_list = []

    result_dict = {}
    for result_i in result_list:
        if topic_str == result_i.get("_source", {}).get("topic_str", ""):
            result_dict = result_i.get("_source", {})
            break
    if result_dict == {}:
        logger.info("error when get result dict")
        return False
    try:
        es_save_result = EsClient(es_ip, es_port).index(index=es_index_2, doc_type=doc_type_2, data=result_dict)
    except Exception as e:
        logger.info("error when save to es: {}".format(e))
        es_save_result = False
    return es_save_result

def es_relocation():
    str_exist_list = []
    match_list = []
    for i in range(1546):
        from_int = i * size
        logger.info("i: {}, from: {}, size: {}".format(i, from_int, size))
        result_list = es_get(from_int, size)
        for j, r in enumerate(result_list):
            r_topic_id = r.get('_source', {}).get('topic_id', '')
            r_topic_str = r.get('_source', {}).get('topic_str', '')
            logger.info("{}: {}".format(str(from_int+j+1), r_topic_str.encode('utf8')))
            # 存过的句子跳过
            if r_topic_str in str_exist_list:
                logger.info("skip !!!!!")
                continue
            # 检查其是否有多个topic_id
            topic_id_list = es_topic_id_more(r_topic_str)
            if len(topic_id_list) == 0:
                logger.info("error(topic_id_list == 0).")
                with open(file_irreg, 'a+') as f:
                    f.writelines(json.dumps(r, ensure_ascii=False, indent=4))
                continue
            elif len(topic_id_list) == 1:
                r_topic_id_best = r_topic_id
            else:
                # 多个topic_id就计算，然后以最佳topic_id存库，且句子、(句子, topic_id)各自append到str_exist_list和match_list；
                # 为了避免程序报错导致str_exist_list和topic_id_match_list缓存丢失，句子和最佳topic_id要实时追加写入文件。
                r_topic_id_best = topic_nor(topic_id_list, r_topic_str)

                if r_topic_id_best != "":
                    str_exist_list.append(r_topic_str)
                    match_list.append((r_topic_str, r_topic_id_best))
                    with open(file_str_exist, 'a+') as f:
                        f.writelines(json.dumps([r_topic_str], indent=4))
                        f.writelines(",\n")
                    with open(file_match, 'a+') as f:
                        f.writelines(json.dumps((r_topic_str, r_topic_id_best), indent=4))
                        f.writelines(",\n")
            save_result = es_save(r_topic_str, r_topic_id_best)
            logger.info("es save result: {}".format(save_result))

if __name__ == "__main__":
    es_relocation()


