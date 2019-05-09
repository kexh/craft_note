# -*- coding: utf-8 -*-
'''
@author: kexh
@update: 2017/11/02
'''

test_tag = False
page_limit = 20
################### 1. 请求接收和转发 ###########################
servers_dict = {
    "backstage_configuration_entrance": ("localhost", "8881"),
    "semantic_main_entrance": ("192.168.0.1", "8881"),
    "semantic_wechat_entrance": ("192.168.0.2", "8881")
}
# fragments 转发时的映射关系
fragments = {
    "test": ("/amber/", "/wchat/dialogue/"),#"/amber_conf/test/",
    "save": "/es_save/"
    # "/configure/save/": "/amber_conf/save/"
    # "/configure/sync_reminder/": "/amber_conf/sync_reminder/"
}
#########################################################

##################### 2. 数据库操作相关 ######################
DB_NAME = "semantic_conf_memory"
DB_IP = "192.168.0.16"
DB_PORT = "3306"
DB_USER = "root"
DB_PWD = "123456"

servers_db = {
    "bg_conf_center": 0, # db name: "semantic_conf_memory"
    # "test_server": 1,
    # "online_server": 2,
}
table_main = "amber_conf_q_sentence"
table_base = ["amber_conf_q_sentence", "amber_conf_a_sentence", "amber_conf_para_sentence"]
columns_common = {
    # in "amber_conf_q_sentence":
    # columns = columns + ["sync_status"] if int(self.tag)==0 else columns + ["local_id"]
    "amber_conf_q_sentence": ["id", "save_time", "q_sentence", "emotion_type", "emotion_target",
                              "emotion_polar", "m_intent_type", "q_sentence_priority"],
    "amber_conf_a_sentence": ["id", "a_sentence", "favor_num", "mood_num", "apply_scene",
                              "save_time", "bg_id"],
    "amber_conf_para_sentence": ["id", "para_sentence", "enable", "score", "save_time", "bg_id"],
}
#########################################################

################### 3. scripts_** ###########################
# old: scripts_**是指semantic_conf_server.py或begin_tonado.py调用conf_**脚本的对应情况。
scripts_dict = {
    '/configure/getdetail/': 'conf_detail',
    '/configure/getlist/': 'conf_list',
    '/configure/save/': 'conf_save',
    '/configure/test/': 'conf_test'
}
# scripts_server = {
#     '/amber_conf/save/': 'conf_save'
# }
#########################################################