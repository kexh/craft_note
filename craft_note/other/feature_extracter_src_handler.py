# -*- coding: utf-8 -*-
'''
@author: kexh
'''
from corpus_feature.corpus_feature_util.corpus_input_getter import input, nlu
from corpus_feature.short_string_features.short_string_features import ssf_main
# from corpus_feature.word_embedding.word_2_vec_test import w2v
from corpus_feature.word_embedding.word_2_vec import w2v
from feature_service_conf import *

SERVICES = {
    "/corpus_feature/": ["sf_sv_svs", "sf_sv", "sf", "sv_svs"],
    "/vec_sim/": ["word_vec", "word_most_sim", "word_words_sim", "sent_sents_sim"]
}

def vec_sim_batch_processing(func):
    def newFunc(_self, data_dict):
        '''
        此装饰器完成的功能：
        "main": 将该字段统一为list。
        "n_sim": 10或其他数字。
        '''
        result_list = []
        word_list = data_dict['main'] if isinstance(data_dict['main'], list) else []
        if func.__name__ == "word_most_sim":
            n_sim = data_dict.get("n_sim", 10)
            logger.info("n_sim: {}".format(n_sim))
        for i, word in enumerate(word_list):
            logger.info("word: {}. ".format(word))
            if func.__name__ == "word_most_sim":
                result_new = func(_self, word, n_sim)
            else:
                result_new = func(_self, word)
            result_list.append(result_new)
        return result_list
    return newFunc

def corpus_feature_batch_processing(func):
    def newFunc(_self, data_dict):
        '''
        此装饰器完成的功能：
        "main": 将该字段统一为list。
        "scheme": "normal"或其他字符串。
        "high_pass_filtered": None或特定字符串。
        "nlu_dict": 从"detail"中取出，假如nlu_dict为空，请求nlu接口补上。
        结果如果是str类型，不叠加，直接返回。
        '''
        result_list = []
        sent_list = data_dict['main'] if isinstance(data_dict['main'], list) else []
        high_pass_filtered = data_dict.get("high_pass_filtered", None)
        if high_pass_filtered not in ["trim", "best"]:
            high_pass_filtered = None
        scheme = data_dict.get("scheme", "normal")
        logger.info("high_pass_filtered: {}. scheme: {}".format(high_pass_filtered, scheme))
        for i, sent in enumerate(sent_list):
            nlu_dict = data_dict['detail'][i] if len(data_dict.get("detail", []))>0 and len((data_dict.get("detail", []))[i])>0 else nlu.get_nlu_dict(sent)
            # logger.info("sent: {}. nlu_dict: {}".format(sent, nlu_dict))
            # nlu_dict = None # todo: this line is for test.
            result_new = func(_self, sent, nlu_dict, high_pass_filtered, scheme)
            if isinstance(result_new, str):
                return result_new
            result_list.append(result_new)
        return result_list
    return newFunc

class VecSim(object):
    def __init__(self):
        pass

    @vec_sim_batch_processing
    def word_vec(self, word, *args):
        word_arr = w2v.get_word_vector(word=word)
        result_word_vec = word_arr.tolist()
        logger.info("result_word_vec of word vec: {}".format(result_word_vec))
        result_dict = dict(word_vec=result_word_vec)
        return result_dict

    @vec_sim_batch_processing
    def word_most_sim(self, word, *args):
        topn = args[0]
        result_words = w2v.get_most_similar(word=word, topn=topn)
        result_dict = dict(word_top_n = result_words)
        return result_dict

    def word_words_sim(self, data_dict):
        # 计算不出的返回-1
        word = data_dict["main"]
        words = data_dict["compare"]
        word_words_sim = [w2v.word_word_cos_sim(word1=word, word2=w) for w in words]
        return dict(word_words_sim = word_words_sim)

    def sent_sents_sim(self, data_dict):
        # 计算不出的返回-1
        str_main = data_dict["main"]# if len(data_dict.get("detail", []))>0 and len((data_dict.get("detail", []))[i])>0
        nlu_dic = data_dict["main_detail"] if len(data_dict.get("main_detail", []))>0 else nlu.get_nlu_dict(str_main)
        if len(data_dict.get("compare_detail", []))>0 and data_dict.get("compare_detail", []) != [{}]:
            nlu_dics = data_dict["compare_detail"]
        else:
            nlu_dics = []
            str_compare = data_dict["compare"]
            for str_ori in str_compare:
                nlu_dics.append(nlu.get_nlu_dict(str_ori))
        sent_sents_sim = [w2v.sent_sent_cos_sim_from_nlu(nlu_dic1=nlu_dic, nlu_dic2=nd) for nd in nlu_dics]
        return dict(sent_sents_sim = sent_sents_sim)

class CorpusFeature(object):
    def __init__(self):
        pass

    @corpus_feature_batch_processing
    def sf_sv_svs(self, sent, nlu_dict, *args):
        ssf_result = ssf_main(sent, nlu_dict)
        if isinstance(ssf_result, str):
            return ssf_result
        else:
            result_dict = ssf_result
        high_pass_filtered = args[0]
        scheme = args[1]
        try:
            word_2_vec_result = w2v.get_sent_vec_and_strenc_from_nlu(nlu_dic=nlu_dict, svs=True, prec=7,
                                        interv=0.05, scheme=scheme, high_pass_filtered=high_pass_filtered)
        except Exception as e:
            logger.info("error when run sv method: {}".format(str(e)))
            word_2_vec_result = str(e)
        if isinstance(word_2_vec_result, str) == False:# or isinstance(word_2_vec_result, str) == False:
            svs, sv_arr = word_2_vec_result
            sv = sv_arr.tolist()
            logger.info("success when run sv method.")
        else:
            svs = ""
            sv = []
            logger.info("word_2_ver_result may skip and mark error here: {}".format(word_2_vec_result))
        result_dict.update(dict(topic_svs = svs, topic_sv = sv))
        return result_dict

    @corpus_feature_batch_processing
    def sf_sv(self, sent, nlu_dict, *args):
        ssf_result = ssf_main(sent, nlu_dict)
        if isinstance(ssf_result, str):
            return ssf_result
        else:
            result_dict = ssf_result
        high_pass_filtered = args[0]
        scheme = args[1]
        try:
            word_2_vec_result = w2v.get_sent_vec_and_strenc_from_nlu(nlu_dic=nlu_dict, svs=False, prec=7, interv=0.05, scheme=scheme, high_pass_filtered=high_pass_filtered)
        except Exception as e:
            logger.info("error when run sv method: {}".format(str(e)))
            word_2_vec_result = str(e)
        if isinstance(word_2_vec_result, str) == False:# or isinstance(word_2_vec_result, str) == False:
            _, sv_arr = word_2_vec_result
            sv = sv_arr.tolist()
            logger.info("success when run sv method.")
        else:
            sv = []
            logger.info("word_2_ver_result may skip and mark error here: {}".format(word_2_vec_result))
        result_dict.update(dict(topic_sv = sv))
        return result_dict

    @corpus_feature_batch_processing
    def sf(self, sent, nlu_dict, *args):
        ssf_result = ssf_main(sent, nlu_dict)
        if isinstance(ssf_result, str):
            return ssf_result
        else:
            result_dict = ssf_result
        return result_dict

    @corpus_feature_batch_processing
    def sv_svs(self, sent, nlu_dict, *args):
        high_pass_filtered = args[0]
        scheme = args[1]
        try:
            word_2_vec_result = w2v.get_sent_vec_and_strenc_from_nlu(nlu_dic=nlu_dict, svs=True, prec=7,
                                        interv=0.05, scheme=scheme, high_pass_filtered=high_pass_filtered)
        except Exception as e:
            logger.info("error when run sv method: {}".format(str(e)))
            word_2_vec_result = str(e)
        if isinstance(word_2_vec_result, str) == False:# or isinstance(word_2_vec_result, str) == False:
            svs, sv_arr = word_2_vec_result
            sv = sv_arr.tolist()
            logger.info("success when run sv method.")
        else:
            svs = ""
            sv = []
            logger.info("word_2_ver_result may skip and mark error here: {}".format(word_2_vec_result))
        result_dict = dict(topic_svs = svs, topic_sv = sv)
        return result_dict

corpus_feature = CorpusFeature()
vec_sim = VecSim()

def comb_output(transition_data):
    if isinstance(transition_data, str):
        ans_dict = dict(code=2100, code_description=transition_data, data={})
    else:
        ans_dict = dict(code=2000, code_description="", data=transition_data)
    return ans_dict

def run(path, req):
    parse_result = input.parse_input(path, req)
    if isinstance(parse_result, tuple):
        if parse_result[0] == "/corpus_feature/":
            data = getattr(corpus_feature, parse_result[1])(parse_result[2])
            logger.info("4785421")
        elif parse_result[0] == "/vec_sim/":
            data = getattr(vec_sim, parse_result[1])(parse_result[2])
        else:
            data = error_list[2]
        return comb_output(data)
    else:
        return comb_output(parse_result)
