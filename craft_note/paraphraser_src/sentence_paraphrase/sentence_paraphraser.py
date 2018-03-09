# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/15
'''
import copy
import json
import gevent
from gevent import monkey
monkey.patch_all()
import importlib
import traceback
import collections
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from common.logger import logger
from paraphraser_conf import *
from sentence_paraphrase.candidate_selection.candidate_selecting import CandidateSelector


class SentenceParaphraser(object):
    def __init__(self):
        self.candidate_selector = CandidateSelector()
        self.trans_dict = dict()
        for i, site_path in enumerate(scripts_list):
            trans_module = importlib.import_module(crawler_dir + site_path[1])
            Trans = getattr(trans_module, 'SiteTranslator')
            cls_obj = Trans()
            self.trans_dict[site_path[0]] = cls_obj

    @exeTime
    def trans_imp(self, sent, site_path, origin_lang_code, target_lang_code):
        cls_obj = self.trans_dict[site_path[0]]
        # logger.info('{}, {}, {}'.format(origin_lang_code, target_lang_code, sent))
        data = cls_obj.translate(sent, origin_lang_code, target_lang_code)
        return data

    @exeTime
    def concurrent_to_pivoting_langs(self, origin_info):
        '''
        1. 每循环到一个新的site实例化它对应的类；属性和方法在循环该site的各个lang时再做处理。
        2. 单个线程如果超过timeout时间拿不到数据，将不收集该线程结果，但更新bad_resp_sites的值。
        3. bad_resp_sites中的单个site有3次或以上记录，就会被跳过。
        4. result设置为set类型，不做加锁处理。
        '''
        pivoting_results = set()
        bad_resp_sites = dict()
        # pool = ThreadPoolExecutor(len(LANG_CODE_DICT_2) * len(scripts_list))
        lang_jobs = []
        logger.info("count of pool is: {}".format(len(LANG_CODE_DICT_2) * len(scripts_list)))# 21
        sent = origin_info[0]
        for i, site_path in enumerate(scripts_list):
            for lang in LANG_CODE_DICT_2:
                if bad_resp_sites.get(site_path[0], 0) >= 3:
                    continue
                origin_lang_code = LANG_CODE_DICT_1.values()[0][i]
                target_lang_code = LANG_CODE_DICT_2[lang][i]
                try:
                    lang_jobs.append((lang, gevent.spawn(self.trans_imp, sent, site_path, origin_lang_code, target_lang_code)))
                    # p = pool.submit(self.trans_imp, sent, site_path, origin_lang_code, target_lang_code)
                    # pivoting_results.add((lang, p.result(timeout=timeout).encode('utf-8')))
                except Exception as e:
                    logger.info("timeout or error here(may skip), {}: {}".format(site_path[0], str(e)))
                    bad_resp_sites.update({site_path[0]: bad_resp_sites.get(site_path[0], 0) + 1})
        gevent.joinall([lang_job[1] for lang_job in lang_jobs], timeout=timeout)
        for (lang, job) in lang_jobs:
            job_value = job.value
            if job_value:
                pivoting_results.add((lang, job_value.encode('utf-8')))
        logger.info("len of pivoting_results: {}. bad_resp_sites: {}".format(len(pivoting_results), bad_resp_sites))
        return pivoting_results, bad_resp_sites

    @exeTime
    def concurrent_back_to_src_lang(self, sent_list, bad_resp_sites):
        '''
        主体思路参见concurrent_to_pivoting_langs.
        '''
        back_to_src_result = set()
        jobs = []
        jobs_2 = []
        sum = 0
        logger.info("count of pool is: {}".format(len(sent_list) * len(scripts_list)))# 63
        # sum and jobs_2: for fix"Connection pool is full, discarding connection"
        for i, site_path in enumerate(scripts_list):
            for (lang, sent) in sent_list:
                sum = sum + 1
                if bad_resp_sites.get(site_path[0], 0) >= 3:
                    continue
                origin_lang_code = LANG_CODE_DICT_2[lang][i]
                target_lang_code = LANG_CODE_DICT_1.values()[0][i]
                try:
                    if sum <= 50:
                        jobs.append(gevent.spawn(self.trans_imp, sent, site_path, origin_lang_code, target_lang_code))
                    else:
                        jobs_2.append(gevent.spawn(self.trans_imp, sent, site_path, origin_lang_code, target_lang_code))
                except Exception as e:
                    logger.info("timeout or error here(may skip), {}: {}".format(site_path[0], str(e)))
        gevent.joinall(jobs, timeout=timeout)
        gevent.joinall(jobs_2, timeout=timeout)
        for job in (jobs+jobs_2):
            job_value = job.value
            if job_value:
                back_to_src_result.add(('chinese', job_value.encode('utf-8')))
        logger.info("len of results: {}. ".format(len(back_to_src_result)))
        return back_to_src_result

    def remove_trailing_punc(self, sent):
        """移除句子末尾的标点符号"""
        assert isinstance(sent, str), type(sent)  # just make sure of the encoding
        unicode_sent = sent.decode('utf-8')
        if unicode_sent[-1] in PUNCS:
            unicode_sent = unicode_sent[:-1]
        return unicode_sent.encode('utf-8')

    @exeTime
    def candidate_forward(self, sent, concur_back_res, **kw):
        multi_ref = kw['multi_ref']
        smoothing_func = kw['smoothing_func']
        weights = kw['weights']
        ensemble_mode = kw['ensemble_mode']
        mode = kw.get('mode', 'mbr_char')
        top_k = len(concur_back_res)

        concur_back_res = {self.remove_trailing_punc(tp[1]) for tp in concur_back_res}

        if not ensemble_mode:
            if mode == 'mbr_char':
                results = self.candidate_selector.get_candidates_by_mbr(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}),
                                                                        mbr_mode='char',
                                                                        top_k=top_k, multi_ref=multi_ref,
                                                                        smoothing_function=smoothing_func,
                                                                        weights=weights)
            elif mode == 'mbr_word':
                results = self.candidate_selector.get_candidates_by_mbr(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}),
                                                                        mbr_mode='word', top_k=top_k,
                                                                        multi_ref=multi_ref,
                                                                        smoothing_function=smoothing_func,
                                                                        weights=weights)
            elif mode == 'jaccard':
                results = self.candidate_selector.get_candidates_by_jaccard(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}), top_k=top_k)
            elif mode == 'char':
                results = self.candidate_selector.get_candidates_by_char(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}), top_k=top_k)
            elif mode == 'pos':
                results = self.candidate_selector.get_candidates_by_pos(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}), top_k=top_k)
            else:
                results = []
        else:
            try:
                results_mbr_char = self.candidate_selector.get_candidates_by_mbr(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}),
                                                                                 mbr_mode='char',
                                                                                 top_k=top_k, multi_ref=multi_ref,
                                                                                 smoothing_function=smoothing_func,
                                                                                 weights=weights)
                results_mbr_word = self.candidate_selector.get_candidates_by_mbr(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}),
                                                                                 mbr_mode='word', top_k=top_k,
                                                                                 multi_ref=multi_ref,
                                                                                 smoothing_function=smoothing_func,
                                                                                 weights=weights)
                results_jaccard = self.candidate_selector.get_candidates_by_jaccard(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}),
                                                                                    top_k=top_k)
                results_char = self.candidate_selector.get_candidates_by_char(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}),
                                                                              top_k=top_k)
                results_pos = self.candidate_selector.get_candidates_by_pos(sent=sent, candidates=(
                    copy.deepcopy(concur_back_res) - {sent}),
                                                                            top_k=top_k)
                results = self._merge_results(
                    [results_mbr_char, results_mbr_word, results_jaccard, results_char, results_pos], top_k=top_k)
            except Exception as e:
                results = []
                logger.exception(traceback.print_exc())
        results = [r.decode('utf-8') for r in results][:10]
        return results

    def _convert_web(self, data):
        """用于将任意数据结构中的unicode string转换成byte string"""
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self._convert_web, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self._convert_web, data))
        else:
            return data

    def paraphrase(self, sent, **kw):
        # 目前只用到了sent的值。
        pivoting_langs, bad_resp_sites = self.concurrent_to_pivoting_langs(origin_info=(sent, 'chinese'))
        concur_back_res = self.concurrent_back_to_src_lang(sent_list=pivoting_langs, bad_resp_sites=bad_resp_sites)
        results = self.candidate_forward(sent, concur_back_res, **kw)
        # if synonym_replacement:
        #     # replaced_results = SentenceParaphraser.batch_replace_bigram_synonym(results)
        #     replaced_results = []
        # else:
        #     replaced_results = []
        # if lm_filtering:  # let us do the language filtering
        #     # lm_filtered_results = sorted([(sent, klm.score(sent)) for sent in results], key=lambda e: e[1], reverse=True)[:lm_top_k]
        #     lm_filtered_results = []
        # else:
        #     lm_filtered_results = []
        replaced_results = []
        lm_filtered_results = []
        data = {
            u'paraphrases': results,
            u"candidates": list(concur_back_res),
            u'lm_filtered_paraphrases': lm_filtered_results,
            u"replaced_paraphrases": replaced_results
        }
        return data#self._convert_web(data)

sentence_paraphraser = SentenceParaphraser()
def run(data):
    '''
    保持原有的字段解析不变。
    '''
    ask = json.loads(data)
    sent = ask['sent'] if 'sent' in ask else u"这个句子泛化算法比较靠谱"
    mode = ask['mode'] if 'mode' in ask else u"mbr_char"
    top_k = int(ask['top_k']) if 'top_k' in ask else 15
    multi_ref = (ask['multi_ref'] == u"True") if 'multi_ref' in ask else False
    smoothing_func = int(ask['smoothing_func']) if 'smoothing_func' in ask else 2
    weights = tuple(
        map(float, ask['weights'].split(u" ")) if "weights" in ask else [0.35, 0.25, 0.2, 0.2])
    ensemble_mode = (ask['ensemble_mode'] == u"True") if 'ensemble_mode' in ask else False
    lm_filtering = (ask['lm_filtering'] == u"True") if 'lm_filtering' in ask else False
    synonym_replacement = (ask['replace_synonym'] == u"True") if "replace_synonym" in ask else True
    lm_top_k = int(ask['lm_top_k']) if 'lm_top_k' in ask else int(top_k * 2 / 3)

    result = sentence_paraphraser.paraphrase(
        sent.encode('utf-8'),
        mode=mode.encode('utf-8'), top_k=top_k, lm_top_k=lm_top_k, multi_ref=multi_ref,
        smoothing_func=smoothing_func, weights=weights, ensemble_mode=ensemble_mode,
        lm_filtering=lm_filtering, synonym_replacement=synonym_replacement)
    return result

if __name__ == "__main__":
    data = json.dumps({"sent": "我喜欢吃紫色的葡萄"})
    result = run(data)
    print result

