# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/25
'''
import re
from common.logger import logger
from media_director_conf import exeTime

def slugify(match_obj):
    match_str = match_obj.group(0)
    logger.info("match_str: {}".format(match_str))
    return ''

class MediaSlot(object):
    @property
    def subModulePropertySetter(self):
        return self._subModulePropertySetter

    @subModulePropertySetter.setter
    def subModulePropertySetter(self, value):
        self._subModulePropertySetter = value

    @property
    def random_re_list(self):
        return self._random_re_list

    @random_re_list.setter
    def random_re_list(self, value):
        self._random_re_list = value

    @property
    def slugify_re_list(self):
        return self._slugify_re_list

    @slugify_re_list.setter
    def slugify_re_list(self, value):
        self._slugify_re_list = value

    @property
    def property_permitted_dict(self):
        return self._property_permitted_dict

    @property_permitted_dict.setter
    def property_permitted_dict(self, value):
        self._property_permitted_dict = value

    @property
    def output_propertys(self):
        return self._output_propertys

    @output_propertys.setter
    def output_propertys(self, value):
        self._output_propertys = value

    def random_play_check(self, query):
        for re_str in self.random_re_list:
            re_compiled = re.compile(re_str)
            re_result = re_compiled.search(query)
            if re_result != None:
                logger.info("true here and the word is: {}. re_str: {}".format(re_result.group(), re_str))
                return True
        return False

    def direction_check(self, input_obj):
        # 判断正向意图和反向意图，去掉一些无用的词，变成包含关键信息的不完整的句子
        # 值替换、屏蔽词.
        # “琥珀”； “琥珀自己的歌”
        director_query = input_obj.query
        director_str = director_query
        for re_str in self.slugify_re_list:
            director_str_temp = re.sub(re_str, slugify, director_query)
            if len(director_str) > len(director_str_temp) and len(director_str_temp)>0:
                director_str = director_str_temp
        logger.info('after slugify re: {}'.format(director_str))
        reverse_director_query = ""  # "不要播放一首周杰伦的七里香"
        hupo_sing = []
        # if "琥珀你自己的歌" in input_obj.query or "唱你自己的" in input_obj.query:
        hupo_tag = False
        if "singer" in self.property_permitted_dict and hupo_tag==True:
            hupo_sing = [{'singer': ["琥珀"]}]
        return director_str, reverse_director_query, hupo_sing

    def direction_combine(self, hupo_sing):
        '''
        output_params格式：
        [
            {},# musicDirector
            {}# musicReverseDirector
        ]
        '''

        # todo：槽位结果中不包括的词需要用到正则之类的方法得到，然后写入标签
        # todo: use self.input_getter here
        # todo：假如hupo_sing歌手名有值，那把原先的值都替换成琥珀；其余的正向和反向各自合并
        output_params = list()
        if hupo_sing != []:
            output_params = hupo_sing
        else:
            if "director_obj" in self.__dict__:
                output_params_dict_1 = self.get_propertys(self.director_obj)
                output_params.append(output_params_dict_1)
            else:
                output_params.append({})
            if "reverse_director_obj" in self.__dict__:
                output_params_dict_2 = self.get_propertys(self.reverse_director_obj)
                output_params.append(output_params_dict_2)
        return output_params

    def set_propertys(self, sub_module_ps, slot_result):
        '''
        根据slot_result对sub_module_ps(实例化了的subModulePropertySetter)进行属性设置
        # 关于以下两种写法之改用后一种的原因： 在get_propertys时能够方便的拿到触发过的属性
        "if hasattr(sub_module_ps, slot):"（这种需要在sub_module_ps.__init__中设置好各个属性的初始值）
        "if slot in sub_module_ps.property_permitted_dict:"
        '''
        slots = slot_result.keys()
        for slot in slots:
            if slot in self.property_permitted_dict:
                sub_slot = list(slot_result[slot].keys())
                try:
                    setattr(sub_module_ps, slot, sub_slot)
                    logger.info("set {} to {}".format(sub_slot, slot))
                except Exception as e:
                    setattr(sub_module_ps, slot, self.property_permitted_dict[slot])
                    logger.info("error when set value to this property('{}') and will skip input value: {}, {}".format(e, slot, sub_slot))
            else:
                logger.info("no in sub_module property list: {}".format(slot))

    def get_propertys(self, sub_module_ps):
        # 此处拿到的是触发过赋值方法的属性
        output_params_dict = dict()
        for key in sub_module_ps.__dict__:
            if key[1:] in self.output_propertys:
                key_new = key[1:]
                output_params_dict[key_new] = sub_module_ps.__dict__[key]
        return output_params_dict

    @exeTime
    def media_slot_main(self, input_obj, slots_extractor_obj):
        '''
        0. random_play_check
        1. direction_check -- director_query; reverse_director_query
        2. self.director_mps -- director_slots;
        3. self.reverse_director_mps -- reverse_director_slots;
        4. self.output_params_check
        '''
        self.input_obj = input_obj
        random_tag = self.random_play_check(self.input_obj.query)
        if random_tag == False:
            logger.info('trie_tree that will use: {}'.format(slots_extractor_obj.trie_tree))
            director_str, reverse_director_str, hupo_sing = self.direction_check(self.input_obj)
            if hupo_sing == []:
                self.director_obj = self.subModulePropertySetter()
                director_slots = slots_extractor_obj.extract_slots(director_str)
                self.set_propertys(self.director_obj, director_slots)
                logger.info((director_slots, vars(self.director_obj)))
                if reverse_director_str != "":
                    self.reverse_director_obj = self.subModulePropertySetter()
                    reverse_director_slots = slots_extractor_obj.extract_slots(reverse_director_str)
                    self.set_propertys(self.reverse_director_obj, reverse_director_slots)
                    logger.info((reverse_director_slots, vars(self.reverse_director_obj)))
            output_params = self.direction_combine(hupo_sing)
            slot_result = ["director", self.input_obj, output_params]
        else:
            slot_result = ["director", self.input_obj, [{}]]
        return slot_result

