# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/25
'''
from common.logger import logger
from media_director.story.story_property_setter import StoryPropertySetter
from media_director.story.story_conf import story_property_permitted_dict, story_output_propertys, random_re_list, slugify_re_list
from media_director.media_director_util.media_slot import MediaSlot
from media_director_conf import exeTime

class StorySlot(MediaSlot):
    def __init__(self):
        self.subModulePropertySetter = StoryPropertySetter
        self.random_re_list = random_re_list
        self.slugify_re_list = slugify_re_list
        self.property_permitted_dict = story_property_permitted_dict
        self.output_propertys = story_output_propertys

    @exeTime
    def slot_main(self, input_obj, slots_extractor_obj):
        return self.media_slot_main(input_obj, slots_extractor_obj)
