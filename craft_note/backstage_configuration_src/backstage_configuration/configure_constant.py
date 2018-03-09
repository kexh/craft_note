#!/usr/bin/python
# coding:utf8

import random
import numpy as np
import pandas
from pandas import DataFrame
from numpy.random import randn as randn

# 定制化数据已删除

class ConfigureConstant(object):
    intent_list = [
                    "问答", ...
                ]
    intent_type_map = {
    "query": "问答",
	...
}


def check_value(**kw):
    '''
    @author: kexh
    @create: 2017/09/28
    以二维的方式（3*3）检查值的合法性。
    :param kw: 涉及emotion_type, emotion_target, emotion_polar三个值（情感类型，情感主体，情感极性）。
               m_intent_type不在这里验证。
    :return: 合法返回True，否则返回False。
    '''
    subject = [u"用户", u"AI", u"其他"]
    polar_list = [u"中性", u"正面", u"负面"]
    user_neutral_emotion = [...]
    user_positive_emotion = [...]
    user_negetive_emotion = [...]
    amber_neutral_emotion = [...]
    amber_positive_emotion = [...]
    amber_negetive_emotion = [...]

    index = subject
    columns = polar_list
    user_emotion = [user_neutral_emotion, user_positive_emotion, user_negetive_emotion]
    amber_emotion = [amber_neutral_emotion, amber_positive_emotion, amber_negetive_emotion]
    data_list = [user_emotion, amber_emotion, amber_emotion]
    target_polar_emotions_df = DataFrame(data_list, index=index, columns=columns)
    emotion_polar = kw.get('emotion_polar', '')
    emotion_target = kw.get('emotion_target', '')
    emotion_type = kw.get('emotion_type', '')

    emotions_list = []
    if emotion_polar in columns and emotion_target in index:
        polar_series = target_polar_emotions_df[emotion_polar]
        emotions_list = polar_series.get(emotion_target)
        # print("emotions_polar in columns and emotions_target in index")
    elif emotion_polar == "" and emotion_target in index:
        target_df =  target_polar_emotions_df.loc[[emotion_target],:]
        emotions_list = target_df.values[0][0] + target_df.values[0][1] + target_df.values[0][2]
        # print("emotions_polar == '' and emotions_target in index")
    elif emotion_target == "" and emotion_polar in columns:
        polar_series = target_polar_emotions_df[emotion_polar]
        emotions_list = polar_series[0] + polar_series[1] + polar_series[2]
        # print("emotions_target == '' and emotions_polar in columns")
    elif emotion_polar == "" and emotion_target == "":
        for i in target_polar_emotions_df.values:
            for j in i:
                emotions_list = emotions_list + j
        # print("emotions_polar and emotions_target == ''.")
    # print(emotion_type, emotions_list)
    if emotion_type in emotions_list or emotion_type == "" or emotions_list == "":
        return True
    return False


if __name__ == '__main__':
    print check_value(emotion_target = u"", emotion_polar = u"", emotion_type = u"喜")

