# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/25
'''
from common.logger import logger
from media_director.music.music_conf import subModuleReDict
from media_director.media_director_util.media_trigger import MediaTrigger

class MusicTrigger(MediaTrigger):
    def __init__(self, compiled):
        self.compiled = compiled

    def trigger_main(self, input_getter):
        # trigger_key = self.check_re(music_trigger_dict, input_getter.query)
        trigger_key = self.check_re(subModuleReDict, input_getter.query)
        if trigger_key:
            slot_result = ["trigger", input_getter, trigger_key]
            return slot_result
        else:
            # 如果trigger判断结果为空，将转入槽位提取环节，此处的return False不会直接用于combine output。
            logger.info("this query has no trigger key: {}".format(input_getter.query))
            return False
