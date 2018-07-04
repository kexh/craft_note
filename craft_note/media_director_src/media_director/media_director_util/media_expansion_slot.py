# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/25
'''
import re
from media_director.media_director_util import ignore
from media_director_conf import exeTime
from common.logger import logger

class ExpansionSlotSelfClarification(object):
    # todo： xx_filter_input_all 要改
    def music_filter_input_all(self, trigger_result, input_obj, direct_forceps_re_list, ignore_list):
         director_str, reverse_director_str = self.filter_input(input_obj, direct_forceps_re_list, ignore_list)
         if trigger_result[0] == "triggers_2":
             director_str = director_str.replace("其他的歌曲", "").replace("其他", "").replace("再继续听", "").replace("继续", "").replace("难听", "").replace("好听", "")
             reverse_director_str = reverse_director_str.replace("其他的歌曲", "").replace("其他", "").replace("再继续听", "").replace("继续", "").replace("难听", "").replace("好听", "")
             logger.info('[updated]director_str: {}; reverse_director_str: {}'.format(director_str, reverse_director_str))
         return director_str, reverse_director_str

    def story_filter_input_all(self, trigger_result, input_obj, direct_forceps_re_list, ignore_list):
         director_str, reverse_director_str = self.filter_input(input_obj, direct_forceps_re_list, ignore_list)
         if trigger_result[0] == "triggers_2":
             director_str = director_str.replace("其他的故事", "").replace("其他", "").replace("再继续听", "").replace("继续", "").replace("难听", "").replace("好听", "")
             reverse_director_str = reverse_director_str.replace("其他的故事", "").replace("其他", "").replace("再继续听", "").replace("继续", "").replace("难听", "").replace("好听", "")
             logger.info('[updated]director_str: {}; reverse_director_str: {}'.format(director_str, reverse_director_str))
         return director_str, reverse_director_str

    def radio_filter_input_all(self, trigger_result, input_obj, direct_forceps_re_list, ignore_list):
         director_str, reverse_director_str = self.filter_input(input_obj, direct_forceps_re_list, ignore_list)
         if trigger_result[0] == "triggers_2":
             director_str = director_str.replace("其他的电台", "").replace("其他的节目", "").replace("其他", "").replace("再继续听", "").replace("继续", "").replace("难听", "").replace("好听", "")
             reverse_director_str = reverse_director_str.replace("其他的电台", "").replace("其他的节目", "").replace("其他", "").replace("再继续听", "").replace("继续", "").replace("难听", "").replace("好听", "")
             logger.info('[updated]director_str: {}; reverse_director_str: {}'.format(director_str, reverse_director_str))
         return director_str, reverse_director_str

    def filter_input(self, input_obj, direct_forceps_re_list, ignore_list):
         '''
         re_result_shortest：存各种re_str结果中最短的；
         query_temp：去掉逗号后进入re_str，经re.sub处理后得到self.re_result；
         '''
         query_origin = input_obj.query
         re_result_shortest = query_origin
         # todo: 值替换、屏蔽词(eg:琥珀琥珀开头)
         query_temp = query_origin#.replace("，", "").replace(",", "")
         for re_str, arg_tag in direct_forceps_re_list:
              re_result = ignore.outpost(query_temp, re_str, arg_tag, input_obj)
              if re_result == "" or len(re_result) == len(query_temp):
                   continue
              re_result = ignore.ignore_1(re_result, ignore_list[0])
              re_result = ignore.ignore_2(re_result, ignore_list[1])
              if len(re_result_shortest) > len(re_result) and re_result != "":
                   re_result_shortest = re_result
         if len(re_result_shortest) == len(query_origin):
              name_result = query_origin
         else:
              name_result = re_result_shortest
         director_str = name_result
         # todo: 增加解析得到包含反向意图的句子。"不要播放一首周杰伦的七里香"
         reverse_director_str = ""
         logger.info('director_str: {}; reverse_director_str: {}'.format(director_str, reverse_director_str))
         return director_str, reverse_director_str

    def filter_set_prop(self, part_speech_permitted_list, input_obj, slot_resut):
        # " for item in slot_resut[key]" format of slot_values: {'周杰伦': [['JAY',[4,7]]],'林俊杰': [['林俊杰',[14,17]]]}
        # format of key_list: ["周杰伦", "林俊杰"]
        # 当word小于等于两个字，假如word在切词列表里头，或这两个字各自在切词列表里头，key留下。todo：后续看下这块有没有算法性能需要优化。
        logger.info("slot_result: {}".format(slot_resut))
        seg_list = input_obj.nlu_result['seg_list']
        part_speech_dict = input_obj.nlu_result['part_speech_dict']
        key_list = list()
        for key in slot_resut:
            # {'song_language': {'english': [['\u82f1\u6587', [1, 3]]]}}
            for item in slot_resut[key]:
                word = item[0]
                if len(word) == 1:
                    # todo: 这块还是要看下能不能更精确过滤 - 1
                    continue
                elif len(word) == 2:
                    if word in seg_list:
                        # todo: 这块还是要看下能不能更精确过滤 - 2: {'song_genre': {'jazz': [['爵士', [0, 2]]]}, 'song': {'乐': [['乐', [2, 3]]]}}
                        key_list.append(key)
                        break
                    part_one = word[0]
                    part_two = word[1]
                    if part_one in seg_list and part_speech_dict[part_one] in part_speech_permitted_list\
                            and part_two in seg_list and part_speech_dict[part_two] in part_speech_permitted_list:
                        key_list.append(key)
                        break
                else:
                    key_list.append(key)
                    break
        return key_list

class ExpansionSlotFilling(ExpansionSlotSelfClarification):
    # @property
    # def trietree_obj(self):
    #     return self._trietree_obj
    #
    # @trietree_obj.setter
    # def trietree_obj(self, value):
    #     self._trietree_obj = value

    @property
    def slot_ref_dict(self):
        return self._slot_ref_dict

    @slot_ref_dict.setter
    def slot_ref_dict(self, value):
        self._slot_ref_dict = value
        self.part_speech_permitted_list = self._slot_ref_dict.get("part_speech_permitted_list", list())
        self.property_permitted_dict = self._slot_ref_dict.get("property_permitted_dict", dict())
        self.word_slot_priority_scoring = self._slot_ref_dict.get("word_slot_priority_scoring", list())
        self.direct_forceps_re_list = self._slot_ref_dict.get("direct_forceps_re_list", list())
        self.direct_forceps_ignore_list = self._slot_ref_dict.get("direct_forceps_ignore_list", list())
        self.subModuleApiRefDict = self._slot_ref_dict.get("subModuleApiRefDict", list())

    @property
    def input_obj(self):
        return self._input_obj

    @input_obj.setter
    def input_obj(self, value):
        self._input_obj = value

    def set_propertys_x1(self, **kw):
        if 'infos_x1' not in kw:
            return kw
        slots_result = kw["infos_x1"]
        property_obj = kw["property_obj"]
        slot_0, slot_values_0 = self.subModule_set_slot_0(self.subModuleApiRefDict, self.input_obj)
        if slot_0 != "" and slot_values_0 != []:
            setattr(property_obj, slot_0, slot_values_0)
        slots = slots_result.keys()
        for slot in slots:
            slot_values = slots_result[slot]
            # 对一些slot做映射，统一到某一个slot；之后再setattr。
            logger.info("slot: {}. slot_values: {}".format(slot, slot_values))
            # slot, slot_values = fil.filter_set_slot(self.subModuleApiRefDict, self.input_obj, slot, slot_values)
            slot, slot_values = self.subModule_set_slot(self.subModuleApiRefDict, self.input_obj, slot, slot_values)
            logger.info("slot: {}. slot_values: {}".format(slot, slot_values))
            if slot in self.property_permitted_dict and slot_values not in[[], ""]:
                try:
                    setattr(property_obj, slot, slot_values)
                    logger.info("set {} to {} success.".format(slot_values, slot))
                except Exception as e:
                    logger.info("error when set value to this property('{}') and will skip input value: {}, {}".format(e, slot, slot_values))
            else:
                logger.info("no in sub_module property list: {}".format(slot))
        kw.update(dict(property_obj=property_obj))
        return kw

    def set_propertys_x2(self, **kw):
        '''
        关于以下两种写法之改用后一种的原因： 在get_propertys时能够方便的拿到触发过的属性
        "if hasattr(sub_module_ps, slot):"（这种需要在sub_module_ps.__init__中设置好各个属性的初始值）
        "if slot in sub_module_ps.property_permitted_dict:"
        '''
        if 'infos_x2' not in kw:
            return kw
        slots_result = kw["infos_x2"]#trietree_infos
        property_obj = kw["property_obj"]
        slots = slots_result.keys()
        for slot in slots:
            slot_result = slots_result[slot]
            if slot in ["song", "singer", "album", "story_author", "story_subtitle", "story_tag", "story_title", "radio_title"]:
                slot_values = self.filter_set_prop(self.part_speech_permitted_list, self.input_obj, slot_result)
            else:
                slot_values = list(slot_result.keys())
            # 对一些slot做映射，统一到某一个slot；之后再setattr。
            logger.info("[old]slot: {}. slot_values: {}".format(slot, slot_values))
            # slot, slot_values = fil.filter_set_slot(self.subModuleApiRefDict, self.input_obj, slot, slot_values)
            slot, slot_values = self.subModule_set_slot(self.subModuleApiRefDict, self.input_obj, slot, slot_values)
            logger.info("[new]slot: {}. slot_values: {}".format(slot, slot_values))
            if slot in self.property_permitted_dict and slot_values != []:
                try:
                    logger.info("may set {} to {}".format(slot_values, slot))
                    setattr(property_obj, slot, slot_values)
                except Exception as e:
                    logger.info("error when set value to this property('{}') and will skip input value: {}, {}".format(e, slot, slot_values))
            else:
                logger.info("no in sub_module property list or slot values is empty: {}".format(slot))
        kw.update(dict(property_obj=property_obj))
        return kw

    def subModule_set_slot(self, subModuleApiRefDict, input_obj, slot, slot_values):
        # "for value in slot_values" format of slot_values: ["one", "two"]
        return slot, slot_values

    def subModule_set_slot_0(self, subModuleApiRefDict, input_obj):
        return "", []


class SlotExtractor(object):
    def run_by_list(self, submodule_slot_list, property_obj, filtered_str, **kw):
        '''
        property_obj, filtered_str 不写入kw一起传进来，是为了避免出现传值缺失。
        kw：有指令且带了点播信息但字面上拿不到槽位的，通过计算得到infos_dict，并赋值给kw。
        '''
        kw.update(dict(property_obj=property_obj, filtered_str=filtered_str))
        for method_tuple in submodule_slot_list:
            for method in method_tuple:
                # method可能取值为计算，填充(目前只有两种区别，所以Filling是包括了计算和填充)，筛选等的方法名。
                if method not in [True, False]:
                    logger.info("method: {}; kw: {}".format(method, kw))
                    kw = getattr(self, method)(**kw)
                if method == True and vars(kw["property_obj"]) != {}:
                    break
        return kw

    def get_propertys(self, sub_module_ps, output_propertys_list):
        # 此处拿到的是触发过赋值方法的属性
        output_params_dict = dict()
        for key in sub_module_ps.__dict__:
            if key[1:] in output_propertys_list:
                key_new = key[1:]
                output_params_dict[key_new] = sub_module_ps.__dict__[key]
        return output_params_dict

if __name__ == '__main__00':
    from media_director.media_director_util.req_input_getter import InputGetter
    from media_director.music.music_conf import direct_forceps_re_list, direct_forceps_ignore_list
    from media_director_conf import NluExtractor
    ne = NluExtractor()
    query_list = [
        "next_歌手",
        "琥珀唱你自己的歌",
        "唱一首歌,给。",
        "唱一首爱吃的。",
        "唱一个李谷一的歌。",
        "唱一首恋爱，这张。",
        "来来一首周杰伦的听妈妈的话。",
        "哦，聊，表演恋爱手杖。",
        "来一首听妈妈的话。",
        "你唱一个凤凰传奇的那个什么？荷塘月色。",
        "唱个花千骨里的歌。",
        "唱一首歌,2903。",
        "唱一首情歌。",
        "来一首月亮惹的祸。",
        "动感好听的一首歌曲,恭喜你家庭,已经。",
        "来一首蔡依林的豆豆。",
        "干什么呀?老婆,我要听绅士这首歌。",
        "放一首,谈心。",
        "放一首情，七里香。",
        "放一首周杰伦的退后。",
        "放一个小苹果。",
        "放一首,那就这样吧。",
        "点一首陆树铭的一幅老酒。",
        "放一首花之舞。",
        "来一首热血燃烧。",
        "我跟她一首大约在冬季好吗?",
        "放一首小星星吧。",
        "放一首邓紫棋的泡沫。",
        "放一个火,凤凰传奇的荷塘月色。",
        "要听那个陷阱，第二天一大早你。",
        "来一首张杰的歌。",
        "唱一首吧，乖。",
        "放一首粤语版的心痛。",
        "放一首李玉刚的,刚好遇见你。",
        "换一首轻音乐。",
        "播放，二技能大招，全都是同学，亲爱的。",
        "放一首薛之谦的动物世界。",
        "放一首父亲作的散文诗。",
        "放一首,缘尽世间。",
        "放一首红，安到新亚梦。",
        "来一首海贼王的歌。",
        "来一首杨幂和刘恺威的错怪。",
        "放一首光良的。",
        "放一首小明卫浴的核爆神曲。",
        "我想听一首悲伤的歌。",
        "背一首梅花。",
        "放一首,刘佳的一个人走。",
        "给我放一首童年。",
        "放一首朴树的平凡之路。",
        "你可不可以放首周杰伦的七里香",
        "我们为何不来首浮夸？",
        "我们可不可以不勇敢，你会不会唱？",
        "你会不会唱我们可不可以不勇敢",
        "给我的妈妈来一首我们可不可以不勇敢",
    ]
    # query_origin = "播放周杰伦的七里香"
    for query in ["我想听一首英文歌，做作业听的", "我想听一首周杰伦的七里香"]:#query_list[:1]:#[:1]:
        nlu_result = ne.get_nlu_dict(query)
        data =	{
            "context": {
                "current_query_str": query,
                "qa_infos": [],
                "nlu_result": nlu_result,
                "uid": "10011"
            }
        }
        input_obj = InputGetter()
        print("input: {}".format(data))
        input_obj.parse_input(data=data)
        # director_str = esfilling.filter_input(input_obj, direct_forceps_re_list, ignore_list=direct_forceps_ignore_list)
        # print(director_str)

