# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/25
'''
from common.logger import logger
from media_director.music.music_property_setter import MusicPropertySetter
from media_director.music.music_conf import music_property_permitted_dict, music_output_propertys, random_re_list, slugify_re_list
from media_director.media_director_util.media_slot import MediaSlot
from media_director_conf import exeTime

class MusicSlot(MediaSlot):
	def __init__(self):
		self.subModulePropertySetter = MusicPropertySetter
		self.random_re_list = random_re_list
		self.slugify_re_list = slugify_re_list
		self.property_permitted_dict = music_property_permitted_dict
		self.output_propertys = music_output_propertys

	@exeTime
	def slot_main(self, input_obj, slots_extractor_obj):
		return self.media_slot_main(input_obj, slots_extractor_obj)
