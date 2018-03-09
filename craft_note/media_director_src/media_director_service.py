# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
@author: kexh
@create: 2018/01/25
'''

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
import threading
import tornado.web
from tornado.options import define, options
from tornado.httpserver import HTTPServer

from common.logger import logger
from media_director_conf import *
from media_director import media_director_handler as handler
from slots_extraction.slots_extractor import SlotsExtractor

lock = threading.Lock()
slots_extractor_obj_dict = dict(
    music = SlotsExtractor(tree_4_what="music"),
    story = SlotsExtractor(tree_4_what="story")
)

define('debug', default=True, help='enable debug mode')
define('server', default=host, help='server')
define('port', default=port, help='port')
options.parse_command_line()
logger.info("begin -> {}:{}".format(options.server, options.port))

class MediaDirectorHandler(tornado.web.RequestHandler):
    @exeTime
    def post(self):
        path = self.request.path
        data = self.request.body.decode()
        logger.info("path of request:%s" % (path))
        logger.info("data of request:%s" % (data))
        ans_dict = dict(code=2100, message="", data={})
        try:
            if data:
                ans_dict = handler.run(data, path, slots_extractor_obj_dict)
                logger.info('len and keys in ans_dict: {}, {}'.format(len(ans_dict), ans_dict.keys()))
        except Exception as e:
            logger.info("this req has error: {}".format(str(e)))
            ans_dict = dict(code=4000, message=str(e), data={})
        ans_str = json.dumps(ans_dict, ensure_ascii=False)
        logger.info("ans_str is: {}".format(ans_str))
        self.write(ans_str)

class UpdateTrieTreeHandler(tornado.web.RequestHandler):
    @exeTime
    def post(self):
        path = self.request.path
        data = self.request.body.decode()
        logger.info("path of request:%s" % (path))
        logger.info("data of request:%s" % (data))
        ans_dict = dict(response="")
        try:
            if data:
                lock.acquire()
                slots_extractor_obj_dict['music'].online_update_slots_extractor()
                lock.release()
                ans_dict = dict(response="ok")
        except Exception as e:
            logger.info("this req has error: {}".format(str(e)))
            ans_dict = dict(response=str(e))
        ans_str = json.dumps(ans_dict, ensure_ascii=False)
        self.write(ans_str)

application = tornado.web.Application([
    (r"/media_director/", MediaDirectorHandler),
    (r"/media_story_director/", MediaDirectorHandler),
    (r"/media_music_director/", MediaDirectorHandler),
    (r"/media_poetry_director/", MediaDirectorHandler),
    (r"/update_trietree/", UpdateTrieTreeHandler),
])

