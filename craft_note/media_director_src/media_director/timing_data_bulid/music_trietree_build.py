# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/07/03
'''
import os
import json
import shutil
from settings import SETTING
from media_director_conf import *
from common.net.http_op import HttpOperation
from common.logger import logger

singer_fname = slots_values_json_resource + "/music/" + "singer_2.json" # 包括歌手别名
song_fname = slots_values_json_resource + "/music/" + "song_2.json" # 包括歌曲别名（拔剑神曲《βίοs》，核爆神曲《aLIEz》，断剑神曲《perfect time》，剑鞘神曲《LAST STARDUST》）
album_fname = slots_values_json_resource + "/music/" + "album_2.json"

headers = {
	'content-type': 'application/json'
}

def req(func):
	def newFunc(_self, method):
		all_result_set = set()
		last_five_resp = []
		for page_num in range(MUSIC_DEFAULT_MAX):
			data = func(_self, page_num)
			try:
				resp = HttpOperation.post(url=SETTING.MUSIC_ES_DATA_API, headers=headers, data=json.dumps(data)).text
			except:
				resp = '{}'
			page_result_set = getattr(pd, method)(resp)
			all_result_set = all_result_set | page_result_set
			if page_result_set == set():
				resp = '{}'
			if len(last_five_resp) >= 5:
				del last_five_resp[0]
			last_five_resp.append(resp)
			if last_five_resp == ['{}', '{}', '{}', '{}', '{}']:
				logger.info("will break [{}] req".format(method))
				break
		return all_result_set
	return newFunc

def parse_json(func):
	def newFunc(_self, data):
		try:
			datas = json.loads(data).get("data", {}).get("result", [])
		except:
			datas = []
		results = set()
		for data_dict in datas:
			result = func(_self, data_dict)
			# result_new = set()
			# for r in result:
			# 	r = pr.refine_1(r)
			# 	r = pr.refine_2(r)
			# 	result_new.add(r)
			results = results | result#_new
		return results
	return newFunc

def read(origin_fname, tag):
	all_result_set = set()
	if os.path.exists(origin_fname):
		with open(origin_fname, "r", encoding='utf-8') as f:
			json_obj = json.load(f)
		for word in json_obj[tag]:
			all_result_set.add(word)
	return all_result_set

def write(output_json, origin_fname):
	temp_fname = origin_fname.replace('.json', '_temp.json')
	bak_fname = origin_fname.replace('.json', '_old.json')
	success = 0
	try:
		if os.path.exists(temp_fname):
			logger.info('remove this file: {}'.format(temp_fname))
			os.remove(temp_fname)
		if os.path.exists(bak_fname):
			os.remove(bak_fname)
		with open(temp_fname, 'w') as outfile:
			json.dump(obj=output_json, fp=outfile, ensure_ascii=False, indent=4)
		if os.path.exists(origin_fname):
			logger.info('copy as old file and remove this file: {}'.format(origin_fname))
			shutil.copyfile(origin_fname, bak_fname)
			os.remove(origin_fname)
		logger.info('rename {} to {}'.format(temp_fname, origin_fname))
		os.rename(temp_fname, origin_fname)
		success = 1
	except Exception as e:
		logger.info('{} write fail: {}'.format(origin_fname, str(e)))
	if success == 0:
		if os.path.exists(bak_fname):
			if os.path.exists(origin_fname):
				os.remove(origin_fname)
			shutil.copyfile(bak_fname, origin_fname)

class GetData(object):
	@req
	def req_song(self, page_num):
		data = {
			"index": "eve_song",
			"type": "eve_song",
			"fields": [
				"id", "title", "alias"
			],
			"offset": page_num,
			"limit": MUSIC_PAGE_LIMIT
		}
		return data

	@req
	def req_singer(self, page_num):
		data = {
			"index": "eve_singer",
			"type": "eve_singer",
			"fields": ["id", "name", "alias"],
			"offset": page_num,
			"limit": MUSIC_PAGE_LIMIT
		}
		return data

	@req
	def req_album(self, page_num):
		data = {
			"index": "eve_menu",
			"type": "eve_album",
			"fields": ["id", "title"],
			"offset": page_num,
			"limit": MUSIC_PAGE_LIMIT
		}
		return data

class ParseData(object):
	@parse_json
	def for_song_alias(self, data_dict):
		result = set()
		song_title = data_dict.get("title", "")
		song_alias = set(data_dict.get("alias", []))
		result.add(song_title)
		result = result | song_alias
		return result

	@parse_json
	def for_singer_alias(self, data_dict):
		result = set()
		singer_title = data_dict.get("title", "")
		singer_alias = set(data_dict.get("alias", []))
		result.add(singer_title)
		result = result | singer_alias
		return result

	@parse_json
	def for_album(self, data_dict):
		result = set()
		album_title = data_dict.get("title", "")
		result.add(album_title)
		return result

	def refine_1(self, str_origin):
		return str_origin

	def refine_2(self, str_origin):
		return str_origin

gd = GetData()
pd = ParseData()

@exeTime
def run():
	logger.info("begin to req song data.")
	all_song_alias_set = gd.req_song('for_song_alias')
	logger.info("begin to req singer data.")
	all_singer_alias_set = gd.req_singer('for_singer_alias')
	logger.info("begin to req album data.")
	all_album_set = gd.req_album('for_album')
	# read origin sets
	logger.info("begin to read origin data.")
	all_song_alias_origin_set = read(song_fname, "song")
	all_singer_alias_origin_set = read(singer_fname, "singer")
	all_album_origin_set = read(album_fname, "album")
	# combine new and origin
	logger.info("begin to combine data.")
	all_song_alias_set = all_song_alias_set | all_song_alias_origin_set
	all_singer_alias_set = all_singer_alias_set | all_singer_alias_origin_set
	all_album_set = all_album_set | all_album_origin_set
	# change to output json
	song_alias_output_dict = dict(song=list(all_song_alias_set))
	singer_alias_output_dict = dict(singer=list(all_singer_alias_set))
	album_output_dict = dict(album=list(all_album_set))
	# write combine datas
	logger.info("begin to write data.")
	write(song_alias_output_dict, song_fname)
	write(singer_alias_output_dict, singer_fname)
	write(album_output_dict, album_fname)

if __name__ == "__main__":
	run()

