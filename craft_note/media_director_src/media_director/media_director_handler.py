# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/25
'''
import json
from common.logger import logger
from media_director_conf import *
from media_director.media_director_util.instantiation_subclass import sub_class_dict
from media_director.media_director_util.submodule_input_getter import InputGetter

def comb_output(transition_data, sub_module_name=None):
    '''
    1. type(transition_data): list
    ["trigger"or"director"or"answer", input_obj, output_params or trigger_key]
    2. type(transition_data): str
    "error_msg"
    '''
    if isinstance(transition_data, list) and sub_module_name != None:
        if transition_data[0] == "trigger":
            data = {
                "userId": transition_data[1].client_id,
                "actionList": [
                    {
                        "operation": "/{}/control".format(sub_module_name),
                        "operationFlag": "unfinished",
                        "params": [transition_data[2]],
                        "intent": {
                            "firstIntent": "media",
                            "secondIntent": "{}".format(sub_module_name),
                            "thirdIntent": "/{}/control/{}".format(sub_module_name, transition_data[2])
                        },
                        "respData": {
                            "state": "{}".format(sub_module_name),
                            "reply": "",
                            "replyType": 1
                        }
                    }
                ]
            }
        elif transition_data[0] == "director":
            data = {...
            }
        elif transition_data[0] == "answer":
            data = {...
            }
        else:
            data = {}
        ans_dict = dict(code=0, message="", data=data)
    else:
        ans_dict = dict(code=2100, message=transition_data, data={})
    return ans_dict

def supply(input_getter, output_setter):
    # todo: 这个是走槽位补充的
    output_setter.id = -1# -1用于测试的标识
    return output_setter

def answer(input_getter, output_setter, obj_field_list, machine_state_dict):
    # todo: 这个是走音乐问答的
    output_setter.reply = "music nlg is nearing completion."
    output_params = {
                "default": output_setter.reply,
                }
    return output_params

def run(data, path, slots_extractor_obj_dict):
    input_obj = InputGetter()
    parse_error_msg = input_obj.parse_input(data=data)
    if parse_error_msg != "":
        return comb_output(transition_data=parse_error_msg)
    else:
        logger.info("input_obj.query: {}".format(input_obj.query))
        sub_module_name = path_dict.get(path, "music")
        slots_extractor_obj = slots_extractor_obj_dict.get(sub_module_name, 'music')
        mt = sub_class_dict[(sub_module_name, "trigger")]
        trigger_result = mt.trigger_main(input_obj)
        logger.info("trigger result is: {}.".format(trigger_result))
        if trigger_result != False:
            logger.info("trigger key is: {}.".format(trigger_result[2]))
            return comb_output(transition_data=trigger_result, sub_module_name=sub_module_name)
        else:
            ms = sub_class_dict[(sub_module_name, "slot")]
            slot_result = ms.slot_main(input_obj, slots_extractor_obj)
            # reply_tag = False
            # if reply_tag == True:
            # todo: obj_field_list, machine_state_dict(信息查询，obj_field_list, machine_state_dict)
            #     c_obj_field = list(dict(obj='song_id', field='singer'))
            #     d_machine_state = dict(song_id='-1')
            #     mps = answer(ig, mps, c_obj_field, d_machine_state)
            # else:
            #     mps = supply(ig, mps)
            return comb_output(transition_data=slot_result, sub_module_name=sub_module_name)
