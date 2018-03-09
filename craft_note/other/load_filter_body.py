# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
'''
@author: kexh
@update: 2017/12/06
'''
import os
import copy
import collections
import ConfigParser
from common.logger import logger
from feature_service_conf import *
cf = ConfigParser.ConfigParser()

def load_stop_word():
    stop_word_list = []
    if os.path.exists(stop_word_all_path):
        with open(stop_word_all_path, 'rb') as f:
            stop_word_list = f.readlines()
            stop_word_list = [a.replace("\n", "").replace("\r", "") for a in stop_word_list]
    else:
        logger.info("{} is not exist.".format(stop_word_all_path))
    return stop_word_list

def load_normalized_config_old():
    normalized_dict = {}
    if os.path.exists(normalized_config_all_path):
        cf.read(normalized_config_all_path)
        normalized_dict = dict(cf.items("normalized_config"))
        normalized_dict_temp = copy.copy(normalized_dict)
        for k in normalized_dict_temp:
            value_list = normalized_dict[k].split(" ")
            normalized_dict[k] = value_list
    else:
        logger.info("{} is not exist.".format(normalized_config_all_path))
    return normalized_dict

@exeTime
def load_normalized_config():
    normalized_dict = {}
    nor_tuple_list = []
    if os.path.exists(normalized_config_all_path):
        cf.read(normalized_config_all_path)
        normalized_dict_temp = dict(cf.items("normalized_config"))
        for k in normalized_dict_temp:
            value_list = normalized_dict_temp[k].split(" ")
            for value in value_list:
                nor_tuple_list.append((value, k))
        normalized_defaultdict = collections.defaultdict(list)
        for k, v in nor_tuple_list:
            normalized_defaultdict[k].append(v)
        normalized_dict = dict(normalized_defaultdict)
    else:
        logger.info("{} is not exist.".format(normalized_config_all_path))
    logger.info("len of nor_tuple_list: {}".format(len(nor_tuple_list)))
    return normalized_dict

stop_word_list = load_stop_word()
normalized_dict = load_normalized_config()

if __name__ == "__main__":
    child_node = "自知之明"
    child_dimension = []
    for k in normalized_dict:
        if child_node == k:
            child_dimension = normalized_dict[k]
            break
    print child_dimension
