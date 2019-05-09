# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/02/27
'''
from common.logger import logger

'''
story模块的业务属性值组装与更新。
只针对对应input，在music模块的output生成过程中，才实例化本脚本的StoryPropertySetter类。
'''

class StoryPropertySetter(object):
	# 部分属性只在传入值的类型正确时，才会被setattr；否则保持默认值。
	# age类的值会做结构修改之后再setattr。
	# 写值进来之前需要先检查是否存在该属性：hasattr(StoryPropertySetter, 'story_name')
	def __init__(self):
		'''
        "storyTitle": [],
        "storyAuthor": [],
        "storyCategory": [],
        "storySubcategory": [],
        "storyTag": []
		'''
		pass

	@property
	def story_title(self):
		return self._storyTitle

	@story_title.setter
	def story_title(self, value):
		if isinstance(value, list) == True:
			self._storyTitle = value
		else:
			raise ValueError("story_title value set may incorrect.")

	# 删掉了其他值