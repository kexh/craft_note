# -*- coding: utf-8 -*-
import re

music_property_permitted_dict = dict(
    song = [],
	...
)

music_output_propertys = [
    "song",...
]


##### slot #####

# 这些方法基本继承自ExpansionSlotExtractor(有些进行了方法重写)，但extract_word_slot除外。
# 输出log打在方法里头。
music_slot_list = [
    # ("music_slot_high_grade", "set_propertys_x1", True),
    ("extract_word_slot", "music_do_heuristic_filtering", "set_propertys_x2", False),
    ("slot_fallback", "set_propertys_x1", False)
]
# 不在列表的走标准分比较；在第一个列表里的走最高分比较；在第二个列表里的走最低分比较（后面会把最低分设置低于19）。
music_word_slot_priority_scoring = {
	"singer": (30, 31, 30, [], []),
	"song_genre": (30, 32, 30, ["轻音乐..."], []),
	"song": (29, 29, 29, [], [])
	...
}
music_part_speech_permitted = ["NP", "NN", "...", "QP"]


# deleted
