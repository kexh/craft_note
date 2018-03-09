# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/25
'''
import re
from common.logger import logger
from media_director.story.story_conf import subModuleReDict
from media_director.media_director_util.media_trigger import MediaTrigger

class StoryTrigger(MediaTrigger):
    def __init__(self, compiled):
        self.compiled = compiled

    def trigger_main(self, input_getter):
        trigger_key = self.check_re(subModuleReDict, input_getter.query)
        if trigger_key:
            slot_result = ["trigger", input_getter, trigger_key]
            return slot_result
        else:
            # 如果trigger判断结果为空，将转入槽位提取环节，此处的return False不会直接用于combine output。
            logger.info("this query has no trigger key: {}".format(input_getter.query))
            return False

if __name__ == "__main__":
    from media_director.story.story_conf import test_sent_list
    from media_director.media_director_util.instantiation_subclass import sub_module_compile
    from media_director.media_director_util.submodule_input_getter import InputGetter

    ig = InputGetter()
    compiled = sub_module_compile(subModuleReDict)
    st = StoryTrigger(compiled)
    all_result = []
    for sent in test_sent_list:
        data = {
            "context": {
                "current_query_str": sent
            }
        }
        ig.parse_input(data=data)
        trigger_result = st.trigger_main(ig)
        if trigger_result:
            all_result.append((sent, trigger_result[2]))
        else:
            all_result.append((sent))
    import time
    time.sleep(2)
    for a in all_result:
        print(a)

