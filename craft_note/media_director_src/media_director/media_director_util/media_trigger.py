# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/25
'''
from common.logger import logger

class MediaTrigger(object):
    @property
    def compiled(self):
        return self._compiled

    @compiled.setter
    def compiled(self, value):
        # if isinstance(value, str) == False:
        #     raise ValueError("trie_tree_ref input may incorrect.")
        # logger.info("trie_tree_ref now is: {}".format(value))
        self._compiled = value

    def check_re(self, trigger_dict, query):
        for key in trigger_dict:
            check_result = False
            for re_comp in self.compiled[key]:
                # print(re_comp, type(self.query), self.query)
                re_result = re_comp.search(query)
                if re_result != None:
                    logger.info("true here and the word is: {}".format(re_result.group()))
                    check_result = True
            if check_result == True:
                return key
        return False
