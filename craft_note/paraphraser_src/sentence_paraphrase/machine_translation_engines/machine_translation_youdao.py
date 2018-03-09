# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/17
'''
import urllib
import random
import hashlib
from common.logger import logger
from paraphraser_conf import youdao_trans_url, accounts
from sentence_paraphrase.machine_translation_engines.machine_translation import Translation

class SiteTranslator(Translation):
    def comb_data(self, sent, origin_lang_code, target_lang_code):
        site_accounts = accounts.get("youdao", [])
        i = random.randint(0, len(site_accounts) - 1)
        account_id = site_accounts[i][0]
        account_key = site_accounts[i][1]

        salt = random.randint(32768, 65536)
        sign = account_id + sent + str(salt) + account_key
        m1 = hashlib.md5()
        m1.update(sign)
        sign = m1.hexdigest()
        url = youdao_trans_url + '?appKey=' + account_id + '&q=' + urllib.quote(
            sent) + '&from=' + origin_lang_code + '&to=' + target_lang_code + '&salt=' + str(salt) + '&sign=' + sign
        return url, {}

    def translate(self, sent, origin_lang_code, target_lang_code):
        url, data_dict = self.comb_data(sent, origin_lang_code, target_lang_code)
        resp = self.req_get(url, data_dict)
        if resp != {}:
            try:
                resp = resp['translation'][0]
            except Exception as e:
                resp = ""
                logger.info('error youdao result this time: {}'.format(e))
        else:
            resp = ""
        return resp

