# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/01/15
'''
import time

host = 'localhost'
port = '8888'

timeout = 3
re_run =2
# LANG_CODE的顺序和scripts_list[i][0]的顺序需要对应
PUNCS = [u'。', u'，', u'！', u'？', u'：', u'；', u'.', u',', u'!', u'?', u':', u';']

LANG_CODE_DICT_1 = {
            'chinese': ['zh', 'zh-CN', 'zh-CHS']
}
LANG_CODE_DICT_2 = {
            'english': ['en', 'en', 'EN'],
            'spanish': ['spa', 'es', 'es'],
            'french': ['fra', 'fr', 'fr'],
            'portuguese': ['pt', 'pt', 'pt'],
            'russian': ['ru', 'ru', 'ru'],
            'japanese': ['jp', 'ja', 'ja'],
            'korean': ['kor', 'ko', 'ko']
}

DEFAULT_TRANS_MAP = {'src': 'chinese',
                     'tgts': ['english', 'spanish', 'french', 'portuguese', 'russian', 'japanese', 'korean']}

crawler_dir = "sentence_paraphrase.machine_translation_engines."
# 每个爬虫脚本加个run函数
scripts_list = [
    ("baidu", "machine_translation_baidu"),# "MachineTranslatorBaidu"),
    ("google", "machine_translation_google"),# "MachineTranslatorGoogle"),
    ("youdao", "machine_translation_youdao")# "MachineTranslatorYoudao")
]

accounts = {
    "baidu": [
...
    ],
    "youdao": [
...
    ]
}

nlu_url = "..."
baidu_trans_url = "http://api.fanyi.baidu.com/api/trans/vip/translate"
youdao_trans_url = "http://openapi.youdao.com/api"
google_trans_url = "translate.google.cn"

def exeTime(func):
    def newFunc(*args, **args2):
        t0 = time.time()
        # logger.info("[time]%s when [func]%s start." % (time.strftime("%X", time.localtime()), func.__name__))
        back = func(*args, **args2)
        # logger.info("[time]%s when [func]%s end." % (time.strftime("%X", time.localtime()), func.__name__))
        print("[cost]%.3fs taken for [func]%s." % (time.time() - t0, func.__name__))
        return back
    return newFunc