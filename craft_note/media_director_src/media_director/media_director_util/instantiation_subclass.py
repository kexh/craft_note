# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/02/07
'''
import re
import importlib
from media_director_conf import *
from common.logger import logger
'''
在程序启动时执行以下操作，以减少在线返回的时间：
1. 预先编译re
2. 实例化各个media子模块的Slot和Trigger类
* 偏属性管理的类暂定为input触发后实例化
'''

def sub_module_compile(subModuleReDict):
    subModuleCompiled = dict()
    for key in subModuleReDict:
        compiled_list = []
        for re_str in subModuleReDict[key]:
            compiled_list.append(re.compile(re_str))
        subModuleCompiled[key] = compiled_list
    return subModuleCompiled

@exeTime
def instan_classes():
    sub_class_dict = {}
    for sub_module_name in path_dict.values():
        try:
            tag_conf = importlib.import_module(media_director_dir + "{}.{}_conf".format(sub_module_name, sub_module_name))
            # tag_conf = importlib.import_module(media_director_dir + sub_module_name + "." + sub_module_name + "_" + "conf")
            logger.info("load this tag_conf: {}".format(tag_conf))
            compiled = sub_module_compile(tag_conf.subModuleReDict)
        except Exception as e:
            logger.info("error when load compiled from conf file and sub_module_compile: {}".format(str(e)))
            compiled = []
        for (module_name, class_name) in sub_module:
            module = importlib.import_module(media_director_dir + "{}.{}_{}".format(sub_module_name, sub_module_name, module_name))
            # module = importlib.import_module(media_director_dir + sub_module_name + "." + sub_module_name + "_" + module_name)
            logger.info("load this subclass: {}".format(module))
            if module_name == "slot":
                # 初始化slot子类时需要传入trieTree数据
                cls_obj = getattr(module, sub_module_name.capitalize() + class_name)()
            else:
                # 初始化trigger子类时需要传入子模块已预编译的re
                cls_obj = getattr(module, sub_module_name.capitalize() + class_name)(compiled)
            sub_class_dict[(sub_module_name, module_name)] = cls_obj
    return sub_class_dict

sub_class_dict = instan_classes()

