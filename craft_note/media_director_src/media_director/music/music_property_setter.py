# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/02/11
'''
from common.logger import logger

'''
music模块的业务属性值组装与更新。
只针对对应input，在music模块的output生成过程中，才实例化本脚本的MusicPropertySetter类。
'''

class MusicPropertySetter(object):
	# 部分属性只在传入值的类型正确时，才会被setattr；否则保持默认值。
	# age类的值会做结构修改之后再setattr。
	# 写值进来之前需要先检查是否存在该属性：hasattr(MusicPropertySetter, 'song')
	def __init__(self):
		pass

	@property
	def song(self):
		return self._song

	@song.setter
	def song(self, value):
		if isinstance(value, list) == True:
			self._song = value
		else:
			raise ValueError("song value set may incorrect.")
	# 其他部分已删