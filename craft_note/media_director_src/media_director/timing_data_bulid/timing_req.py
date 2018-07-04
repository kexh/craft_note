# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2018/07/03
'''
import sys
import json
from settings import SETTING
from common.logger import logger
from common.net.http_op import HttpOperation

'''
[timing_req.py usage](story trietree 暂时不需要更新。)
0 4 * * 1 cd /?/AIService_MediaDirector/src/ && python3 timing_req.py --setting-file-name test music
0 8 * * 1 cd /?/AIService_MediaDirector/src/ && python3 timing_req.py --setting-file-name test radio
'''

UpdateTrieTreeHandler = "/update_trietree/"

def req_update_api(tag):
	try:
		ret = HttpOperation.post("http://{}:{}{}".format(SETTING.host, SETTING.port, UpdateTrieTreeHandler),
		                         data=json.dumps({"tag": tag}), timeout=5).text
		result = json.loads(ret).get("response", "fail")
	except Exception as e:
		print("error: {}".format(e))
		result = "fail"
	return result

#
# for tag in path_dict:
# 	result = req_update_api(tag)

if __name__ == "__main__":
	tag = sys.argv[-1]
	result = req_update_api(tag)
	logger.info("result: {}".format(result))

