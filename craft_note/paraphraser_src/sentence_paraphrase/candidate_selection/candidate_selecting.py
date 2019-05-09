# -*- coding: utf-8 -*-
'''
@author: kexh
'''
import copy
import nltk
import numpy
from nltk.translate.bleu_score import SmoothingFunction
from sentence_paraphrase.candidate_selection.basis_nlu import ignore_2, nlu_extractor
from sentence_paraphrase.candidate_selection.spcl_word_weighting import spcl_word_weighting
from sentence_paraphrase.candidate_selection.gensim_weighting import sent_sents_sim_weighting
from paraphraser_conf import *
from common.logger import logger

class CandidateSelector(object):
    def __init__(self):
        pass

    @exeTime
    def get_representative_sents(self, sent, concur_back_res, top_k_outside):
        # bleu 得到top 20（带编号），之后top 20 分别进spcl_weight和sim_weight得到各自的打分，打分相加后再sort。
        bleu_filted_result = self.filter_bleu(sent, concur_back_res)
        nlu_result = nlu_extractor(sent)
        spcl_infos = spcl_word_weighting(sent, bleu_filted_result, nlu_result)
        sim_infos = sent_sents_sim_weighting(sent, bleu_filted_result, nlu_result)
        logger.info("spcl_infos and sim_infos: {}, {}".format(spcl_infos, sim_infos))
        # spcl_infos = None
        if spcl_infos == None or sim_infos == None:
            results_temp = [[sent_temp, -1] for [_, sent_temp] in bleu_filted_result]
        else:
            results_temp = []
            for [i, sent_temp] in bleu_filted_result:
                if sim_infos[i][1] != -1:
                    score = (float(spcl_infos[i][1]) + float(sim_infos[i][1])) / float(1.75)
                    score = round(score, 3)
                else:
                    score = float(-1)
                results_temp.append([sent_temp, score])
        results_temp = sorted(results_temp, key=lambda sent_info : sent_info[1], reverse=True)
        results = [r for r in results_temp][:top_k_outside]
        return results

    @exeTime
    def get_representative_sents_for_short(self, sent, concur_back_res, top_k_outside):
        # 根据测试效果决定不做特殊词的考察，一部分是出现概率较低，另一方面是可能影响同义词扩充效果。
        # top_k_outside为了保证泛化效果，这个值无论是外部传入还是调用conf的，短句自动降三分之一。
        logger.info("go short way this time.")
        top_k_outside = int((top_k_outside * 2) / 3)
        if len(concur_back_res) == 0:
            return []
        concur_back_res_num = [[i, sent_temp] for i, sent_temp in enumerate(concur_back_res)]
        nlu_result = nlu_extractor(sent)
        sim_infos = sent_sents_sim_weighting(sent, concur_back_res_num, nlu_result)
        if sim_infos == None:
            results_temp = [[sent_temp, -1] for sent_temp in concur_back_res]
        else:
            sim_infos_sorted = sorted(sim_infos, key=lambda sent_info : sent_info[1], reverse=True)
            results_temp = [[concur_back_res_num[num][1], score] for [num, score] in sim_infos_sorted]
        results = [r for r in results_temp][:top_k_outside]
        return results

    def filter_bleu(self, sent, concur_back_res):
        concur_back_res = {ignore_2(tp) for tp in concur_back_res}
        candidates = (copy.deepcopy(concur_back_res) - {sent})
        candidates_ = list(candidates)  # candidates里面可能已经有sent，这里确保candidates_ 里面没有sent
        candidates.add(sent)  # 确保candidates里面有sent
        candidates_plus_sent_ = list(candidates)  # candidates_plus_sent_里面确保有sent

        score_array = numpy.zeros(shape=(len(candidates_), len(candidates_plus_sent_)), dtype=numpy.float)
        for i in range(score_array.shape[0]):
            para = list(candidates_[i])
            for j in range(score_array.shape[1]):
                ref = list(candidates_plus_sent_[j])
                try:
                    score_array[i][j] = nltk.translate.bleu_score.sentence_bleu(
                        references=[ref], hypothesis=para, weights=weights, smoothing_function=SmoothingFunction().method2)
                except Exception as e:
                    logger.info('error when get score_array[i][j]: {}, {}. {}'.format(ref, para, e))
                    score_array[i][j] = 0
        sum_array = numpy.sum(score_array, axis=1)
        sort_index_array = numpy.argsort(sum_array)[::-1]
        result = [[i, candidates_[idx]] for i, idx in enumerate(sort_index_array[:top_k_inside])]
        # logger.info("bleu_filted_result: {}".format(result))
        return result

if __name__ == '__main__':
    candidate_selector = CandidateSelector()
    sent = "我喜欢紫葡萄"
    concur_back_res = {'我喜欢吃葡萄紫色，上海产地的。', '我喜欢紫色的葡萄', '我喜欢有紫色的葡萄'}
    results = candidate_selector.get_representative_sents_for_short(sent, concur_back_res, 5)




