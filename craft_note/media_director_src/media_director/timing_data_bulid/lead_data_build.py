# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/07/03
'''
import json
from media_director_conf import path_dict
from timing_data_bulid import music_trietree_build, story_trietree_build, radio_trietree_build
from media_director.media_director_util.trietree_string_matching import TrieTree, PinYinTrieTree

def update_files(sub_module):
	if sub_module == "story":
		story_trietree_build.run()
	elif sub_module == "radio":
		radio_trietree_build.run()
	else:
		music_trietree_build.run()

def update_trees(sub_module):
	if sub_module == "story":
		sub_module_update_trees = dict(story = (TrieTree("story"), PinYinTrieTree("story")))
	elif sub_module == "radio":
		sub_module_update_trees = dict(radio = (TrieTree("radio"), PinYinTrieTree("radio")))
	else:
		sub_module_update_trees = dict(music = (TrieTree("music"), PinYinTrieTree("music")))
	return sub_module_update_trees

def lead_data_build(data):
	tag = json.loads(data).get("tag", "music")
	if tag in path_dict.values():
		update_files(tag)
		trees_dict = update_trees(tag)
	else:
		trees_dict = dict()
	return trees_dict

if __name__ == "__main__":
	slots_extractor_obj_dict = lead_data_build(json.dumps({'tag': 'music'}))
	print(slots_extractor_obj_dict.keys())
