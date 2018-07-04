# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/15
'''
import json
import gevent
import importlib
from common.logger import logger
from paraphraser_conf import *
from sentence_paraphrase.candidate_selection.candidate_selecting import CandidateSelector
from sentence_paraphrase.extender.extend_by_synonym import extend_by_synonym
candidate_selector = CandidateSelector()

def itera_para(func):
    def newFunc(_self, outer_cycle_ref, inner_cycle_ref, **kw):
        '''
        此装饰器完成的功能：
        1. 双层循环
            outer_cycle_ref 指针对不同的api(or 维度)
            inner_cycle_ref 指针对要迭代处理的句子对象列表
        2.
            para_obj 指要泛化的句子，以及语言
            bad_resp_ref 响应情况不太好的api及其响应坏掉的次数（字典类型）
        3. sum and jobs_2: for fix"Connection pool is full, discarding connection"
        4. 保证协程个数大小合适
        5. 拿到job value组成集合
        '''
        resp_results_set = set()
        bad_resp_ref = dict()
        jobs = []
        jobs_2 = []
        count = 0
        # logger.info("count of pool is: {}".format(len(outer_cycle_ref) * len(inner_cycle_ref)))
        for i, site_path in enumerate(outer_cycle_ref):
            for para_obj_origin in inner_cycle_ref:
                if 'sent' in kw:
                    if bad_resp_ref.get(site_path[0], 0) >= 3:
                        continue
                    para_obj = (kw['sent'], LANG_CODE_DICT_1['chinese'][i], LANG_CODE_DICT_2[para_obj_origin][i])
                    job_ref, bad_resp_ref = func(_self, i, site_path, para_obj, bad_resp_ref)
                else:
                    # if bad_resp_ref.get(site_path[0], 0) >= 21:
                    #     continue
                    para_obj = (para_obj_origin[1], para_obj_origin[0], LANG_CODE_DICT_1['chinese'][i])
                    job_ref, bad_resp_ref = func(_self, i, site_path, para_obj, bad_resp_ref)
                count = count + 1
                if job_ref != None:
                    if count <= 35:
                        jobs.append(job_ref)
                    else:
                        jobs_2.append(job_ref)
        gevent.joinall([job for job in jobs], timeout=timeout)
        for job in (jobs+jobs_2):
            job_value = job.value
            if job_value and job_value[1]:
                resp_results_set.add(job_value)
        logger.info("len of itera_para results: {}. bad_resp_ref: {}".format(len(resp_results_set), bad_resp_ref))
        return resp_results_set, bad_resp_ref
    return newFunc

class SentenceParaphraser():
    '''
    1. SentenceParaphraser初始化时，每循环到一个Trans()，则对应的新的site实例化它对应的类；属性和方法在循环该site的各个lang时再做处理。
    2. 单个线程如果超过timeout时间拿不到数据，将不收集该线程结果，但更新bad_resp_sites的值。
    3. bad_resp_ref中的单个site有3次或以上记录，就会被跳过。
    4. result设置为set类型，不做加锁处理。
    '''
    def __init__(self):
        self.trans_dict = dict()
        for i, site_path in enumerate(scripts_list):
            trans_module = importlib.import_module(crawler_dir + site_path[1])
            Trans = getattr(trans_module, 'SiteTranslator')
            cls_obj = Trans()
            self.trans_dict[site_path[0]] = cls_obj

    def trans_imp(self, site_path, sent, origin_lang_code, target_lang_code):
        cls_obj = self.trans_dict[site_path[0]]
        # logger.info('{}, {}, {}'.format(origin_lang_code, target_lang_code, sent))
        try:
            data = cls_obj.translate(sent, origin_lang_code, target_lang_code)
        except Exception as e:
            logger.info("error in this translate: {}".format(str(e)))
            data = ""
        return target_lang_code, data

    @itera_para
    def pivoting_langs(self, i, site_path, para_obj, bad_resp_ref):
        job_ref = None
        sent = para_obj[0]
        if isinstance(sent, bytes):
            sent = str(sent, encoding='utf-8')
        try:
            job_ref = gevent.spawn(self.trans_imp, site_path, sent, para_obj[1], para_obj[2])
        except Exception as e:
            logger.info("timeout or error here(may skip), {}: {}".format(site_path[0], str(e)))
            bad_resp_ref.update({site_path[0]: bad_resp_ref.get(site_path[0], 0) + 1})

        return job_ref, bad_resp_ref

    @itera_para
    def back_to_src_lang(self, i, site_path, para_obj, bad_resp_ref):
        job_ref = None
        sent = para_obj[0]
        if isinstance(sent, bytes):
            sent = str(sent, encoding='utf-8')
        try:
            job_ref = gevent.spawn(self.trans_imp, site_path, sent, para_obj[1], para_obj[2])
        except Exception as e:
            logger.info("timeout or error here(may skip), {}: {}".format(site_path[0], str(e)))
            bad_resp_ref.update({site_path[0]: bad_resp_ref.get(site_path[0], 0) + 1})

        return job_ref, bad_resp_ref

    def paraphrase(self, sent, top_k_outside):
        # todo: bad_resp_ref可以考虑外层也共用
        if isinstance(sent, bytes):
            sent = str(sent, encoding='utf-8')
        # if short_sent_length_a > len(sent):
        #     data = {
        #         "para_sentence_list": [],  # list(concur_back_res_new),
        #         "candidates": [],  # list(concur_back_res_new),
        #         "paraphrases": [],  # list(concur_back_res_new),
        #         "lm_filtered_paraphrases": [],
        #         "paraphrases_score": []
        #     }
        #     return data
        if short_sent_length_a <= len(sent) <= short_sent_length_b:
            # 针对短句：找到同义词列表，先做替换（另一种形式的句子扩充），得到句子列表，再做翻译，汇总所有泛化句，进入短句专用筛选器。
            concur_back_res_new = set()
            pivoting_langs_all = set()
            bad_resp_ref = dict()
            sents_for_trans = extend_by_synonym(sent)
            if len(sents_for_trans) >= synonym_para_no_trans:
                # 匹配到的同义词较多的，还是要翻译原句，不然句子结构太单一。
                concur_back_res_new = sents_for_trans
                pivoting_langs, bad_resp_ref = self.pivoting_langs(scripts_list, LANG_CODE_DICT_2, sent=sent)
                concur_back_res, bad_resp_ref = self.back_to_src_lang(scripts_list, pivoting_langs, bad_resp_ref=bad_resp_ref)
                for _, para_sent in concur_back_res:
                    concur_back_res_new.add(para_sent)
            else:
                # 如果句子还是少，同义词扩充句和原句都翻译。
                if len(sents_for_trans) == 0:
                    logger.info("this one no synonym result")
                else:
                    for sent_new in sents_for_trans:
                        concur_back_res_new.add(sent_new)
                sents_for_trans.add(sent)
                sents_for_trans = list(sents_for_trans)
                for sent_new in sents_for_trans:
                    pivoting_langs_set, bad_resp_ref_temp = self.pivoting_langs(scripts_list, LANG_CODE_DICT_2_for_short, sent=sent_new)
                    pivoting_langs_all.update(pivoting_langs_set)
                    bad_resp_ref.update(bad_resp_ref_temp)
                logger.info("len of pivoting_langs_all: {}".format(len(pivoting_langs_all)))
                for pivoting_langs_tuple in pivoting_langs_all:
                    pivoting_langs = {pivoting_langs_tuple}
                    concur_back_res, bad_resp_ref = self.back_to_src_lang(scripts_list, pivoting_langs, bad_resp_ref=bad_resp_ref)
                    for _, para_sent in concur_back_res:
                        concur_back_res_new.add(para_sent)
            results = candidate_selector.get_representative_sents_for_short(sent, concur_back_res_new, top_k_outside)
        else:
            # 针对其他长度的句子：直接进行翻译，汇总所有泛化句，进入筛选器。
            pivoting_langs, bad_resp_ref = self.pivoting_langs(scripts_list, LANG_CODE_DICT_2, sent=sent)
            concur_back_res, bad_resp_ref = self.back_to_src_lang(scripts_list, pivoting_langs, bad_resp_ref=bad_resp_ref)
            concur_back_res_new = set()
            for _, para_sent in concur_back_res:
                concur_back_res_new.add(para_sent)
            results = candidate_selector.get_representative_sents(sent, concur_back_res_new, top_k_outside)
        paraphrases_results = [r[0] for r in results]
        paraphrases_score = results
        data = {
            # 这么多重复的字段是因为不知道前端用了哪个。sad，历史原因。
            "para_sentence_list": paraphrases_results,#list(concur_back_res_new),
            "candidates": paraphrases_results,#list(concur_back_res_new),
            "paraphrases": paraphrases_results,#list(concur_back_res_new),
            "lm_filtered_paraphrases": paraphrases_score,
            "paraphrases_score": paraphrases_score
        }
        return data

sentence_paraphraser = SentenceParaphraser()
def run(ask_context):
    ask = json.loads(ask_context)
    top_k_outside = top_k_client
    if 'top_k' in ask and 1 <= int(ask['top_k']) <= 20 and int(ask['top_k']) != 15:
        top_k_outside = int(ask['top_k'])
    if 'sents' in ask and isinstance(ask['sents'], list):
        main = []
        for sent in ask['sents']:
            try:
                data = sentence_paraphraser.paraphrase(sent, top_k_outside)
                data.update(dict(sub_code=2000, sub_message=""))
            except Exception as e:
                sub_message = str(e)
                data = (dict(sub_code=2100, sub_message=sub_message))
            main.append(data)
        data_all = dict(code=2000, message="", main=main)
        return data_all
    if 'sent' not in ask:
        data = dict(code=2100, message="no sentence here")
    else:
        sent = ask['sent']
        try:
            data = sentence_paraphraser.paraphrase(sent, top_k_outside)
            # logger.info("here 3333: {}".format(data))
            data.update(dict(code=2000))
            # logger.info("here 3344: {}".format(data))
        except Exception as e:
            logger.info("error here: {}".format(str(e)))
            data = dict(code=2100, message=str(e))
    return data

if __name__ == "__main__":
    sents = ["今天北京天气怎样",]
    for sent in sents:#1]:
        data = json.dumps({
                "lm_filtering": "True",
                "lm_top_k": "10",
                "mode": "mbr_char",
                "multi_ref": "False",
                "sent": "今天北京天气怎样",
                "smoothing_func": "2",
                "top_k": "15"
            })
        # data = json.dumps({"sent": sent})
        result = run(data)
        print(sent, result.get('paraphrases', ': empty result here'))
