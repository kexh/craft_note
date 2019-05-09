# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/25
'''
import time
import os.path

host = 'localhost'
port = '8888'

media_director_dir = "media_director."

path_dict = {
	"/media_music_director/": "music",
	"/media_story_director/": "story"#,
	# "/media_poetry_director/": "poetry",
}

sub_module = [
    # (未带子模块前缀的module_name, 未带子模块前缀的class_name)
    ("trigger", "Trigger"),
    ("slot", "Slot")
    # ("slot_2", "Slot")
]

sources_root = os.path.abspath(os.path.dirname(__file__))
att_path = os.path.join(os.path.dirname(sources_root), 'data','att_publish',)
att_dir = "..data.att_publish."
# music_conf = os.path.join(att_path, 'music', 'music_conf.py')


input_included_dict = dict(
	query="",
	nlu_result=dict(),
	qa_infos=list(),
	client_id=0
)

def exeTime(func):
    def newFunc(*args, **args2):
        t0 = time.time()
        # logger.info("[time]%s when [func]%s start." % (time.strftime("%X", time.localtime()), func.__name__))
        back = func(*args, **args2)
        # logger.info("[time]%s when [func]%s end." % (time.strftime("%X", time.localtime()), func.__name__))
        print("[cost]%.3fs taken for [func]%s." % (time.time() - t0, func.__name__))
        return back
    return newFunc

