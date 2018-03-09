# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/02/12
'''
import json
from media_director_conf import input_included_dict
from common.logger import logger

'''
根据api所接收的外部值，对本子模块逻辑处理时需要使用到的参数进行值的设置。
子模块input触发时才实例化本脚本的InputGetter类。
'''

class InputGetter(object):
	# 部分属性只在传入值的类型正确时，才会被更新值；否则保持默认值。

	def __init__(self):
		# todo： 调取机器实时状态的api得到的字段，可以包括进InputGetter，但不在parse_input里解析。
		pass

	def parse_input(self, **kw):
		'''
		:param kw: data=data, media_context=media_context
		[qa_infos & media_context]
		qa_infos是dm传过来的上下文信息，一般够用了。
		media_context作为预留字段，主动调语义的其它api拿到对话上下文的。
		'''
		data = kw.get('data')
		if isinstance(data, str):
			data_dict = json.loads(data)
		else:
			data_dict = data
		if isinstance(data_dict, dict) == False:
			# self.query = ""
			return "input sentence is empty."
		else:
			input_dict = dict(
			query = data_dict.get("context", {}).get("current_query_str", input_included_dict["query"]),
			nlu_result = data_dict.get("context", {}).get("nlu_result", input_included_dict["nlu_result"]),
			qa_infos = data_dict.get("context", {}).get("qa_infos", input_included_dict["qa_infos"]),
			client_id = int(data_dict.get("context", {}).get("uid", input_included_dict["client_id"]))
			# media_context = kw.get('media_context', [])
			)
			for key in input_dict:
				if key in input_included_dict:
					try:
						setattr(self, key, input_dict[key])
						logger.info("set {} to {}".format(input_dict[key], key))
					except Exception as e:
						setattr(self, key, input_included_dict[key])
						logger.info("error this input('{}') and will skip input value: {}, {}".format(e, key, input_dict[key]))
			return ""

	@property
	def query(self):
		return self._query

	@query.setter
	def query(self, value):
		if isinstance(value, str) == True:
			# logger.info("query now is: {}".format(value))
			self._query = value
		else:
			raise ValueError("query input may incorrect.")

	@property
	def nlu_result(self):
		return self._nlu_result

	@nlu_result.setter
	def nlu_result(self, value):
		if isinstance(value, dict) == True:
			# logger.info("nlu_result now is: {}".format(value))
			self._nlu_result = value
		else:
			raise ValueError("nlu_result input may incorrect.")

	@property
	def qa_infos(self):
		return self._qa_infos

	@qa_infos.setter
	def qa_infos(self, value):
		if isinstance(value, list) == True:
			# logger.info("qa_infos now is: {}".format(value))
			self._qa_infos = value
		else:
			raise ValueError("qa_infos input may incorrect.")

	@property
	def media_context(self):
		return self._media_context

	@media_context.setter
	def media_context(self, value):
		if isinstance(value, list) == True:
			# logger.info("media_context now is: {}".format(value))
			self._media_context = value
		else:
			raise ValueError("media_context input may incorrect.")

	@property
	def client_id(self):
		return self._client_id

	@client_id.setter
	def client_id(self, value):
		if isinstance(value, int) == True:
			# logger.info("client_id now is: {}".format(value))
			self._client_id = value
		else:
			raise ValueError("client_id input may incorrect: {}".format(value))
