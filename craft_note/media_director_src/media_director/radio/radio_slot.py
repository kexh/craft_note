# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/06/26
'''
from common.logger import logger
from media_director.radio.radio_property_setter import RadioPropertySetter
from media_director.radio.radio_conf import *
from media_director.radio.radio_api_ref import tag_dict
from media_director.media_director_util.media_word_slot import WordSlotFilling
from media_director.media_director_util.media_expansion_slot import ExpansionSlotFilling, SlotExtractor


class RadioSlot(WordSlotFilling, ExpansionSlotFilling, SlotExtractor):
	def __init__(self):
		self.slot_ref_dict = dict(
			part_speech_permitted_list=radio_part_speech_permitted_list,
			property_permitted_dict=radio_property_permitted_dict,
			word_slot_priority_scoring=radio_word_slot_priority_scoring,
			direct_forceps_re_list=direct_forceps_re_list,
			direct_forceps_ignore_list=direct_forceps_ignore_list,
			subModuleApiRefDict=tag_dict
		)

	def slot_fallback(self, **kw):
		# 把前两种没有拿到但是符合语法或正则规则的存到标签里；根据badcase等扩充功能。
		if vars(kw["property_obj"]) == {}:
			filtered_str = kw["filtered_str"]
			new_infos = dict(radio_director_unknown=filtered_str.replace("...", ""))
			kw.update(dict(infos_x1=new_infos))
		return kw

	def subModule_set_slot(self, subModuleApiRefDict, input_obj, slot, slot_values):
		if slot in ["radio_category"]:
			value_list = []
			for value in slot_values:
				if value in subModuleApiRefDict:
					value_list.append(subModuleApiRefDict[value][0])
			return "radio_category", value_list
		return slot, slot_values

	def slot_main(self, input_obj, trietree_obj, pinyin_trietree_obj, trigger_result):
		'''
		[about trigger result update]
		"direct"和"triggers_2"(不包括"random")两类trigger_result会进来，各自可能走的分支包括：
		1. "direct": 继续走"direct"(包括"random"的[{}, {}])；改为"no_media_func"。
		2. "triggers_2"：继续走"triggers_2"；改为"direct"。
		'''
		self.input_obj = input_obj
		self.trietree_obj = trietree_obj
		self.pinyin_trietree_obj = pinyin_trietree_obj
		logger.info('trie_tree and pinyin_trietree this time: {}, {}'.format(self.trietree_obj, self.pinyin_trietree_obj))
		output_params = list()
		director_str, reverse_director_str = self.radio_filter_input_all(trigger_result, self.input_obj,
		                                                                self.direct_forceps_re_list,
		                                                                self.direct_forceps_ignore_list)
		for i, filtered_str in enumerate([director_str, reverse_director_str]):
			output_dict = dict()
			if filtered_str != "":
				property_obj = RadioPropertySetter()
				kw = self.run_by_list(radio_slot_list, property_obj, filtered_str)
				if trigger_result[-1] == "play_favor" and trigger_result[0] == "triggers_2":
					kw = self.run_by_list([("set_propertys_x1", False)], property_obj, filtered_str, infos_x1=dict(favor_first=1))
				output_dict = self.get_propertys(kw["property_obj"], radio_output_propertys)
			if (filtered_str == "" or output_dict == {}) and trigger_result[0] == "triggers_2" and i == 0:
				trigger_result_updated = trigger_result
				return trigger_result_updated
			output_params.append(output_dict)
		trigger_result_updated = ["direct", self.input_obj, output_params]
		return trigger_result_updated


if __name__ == "__main__":
	from media_director.radio.radio_trigger import RadioTrigger
	from media_director.media_director_util.instantiation_subclass import sub_module_compile
	from media_director.media_director_util.req_input_getter import InputGetter
	from media_director.media_director_util.trietree_string_matching import TrieTree, PinYinTrieTree
	from media_director_conf import NluExtractor
	trietree_obj = TrieTree("radio")
	pinyin_trietree_obj = PinYinTrieTree("radio")
	ne = NluExtractor()
	compiled = sub_module_compile(subModuleReDict)
	rt = RadioTrigger(compiled)
	rs = RadioSlot()
	for query in ["..."]:
		nlu_result = ne.get_nlu_dict(query)
		data = {
			"context": {
				"current_query_str": query,
				"qa_infos": [],
				"nlu_result": nlu_result,
				"uid": "13243092346"
			}
		}
		input_obj = InputGetter()
		print("input: {}".format(data))
		input_obj.parse_input(data=data)
		trigger_result = rt.trigger_main(input_obj)
		slot_result = rs.slot_main(input_obj, trietree_obj, pinyin_trietree_obj, trigger_result)
		logger.info("slot result: {}".format(slot_result))
		logger.info("3333")

