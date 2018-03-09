# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
@author: kexh
@create: 2018/01/18
'''
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import json
import tornado.web
from tornado.options import define, options
from tornado.httpserver import HTTPServer

from common.logger import logger
from paraphraser_conf import *
from sentence_paraphrase import sentence_paraphraser as sp

# usage: python paraphraser_service.py --port=8383
define('debug', default=True, help='enable debug mode')
define('server', default=host, help='server')
define('port', default=port, help='port')
options.parse_command_line()
logger.info("begin -> {}:{}".format(options.server, options.port))

class SentParaHandler(tornado.web.RequestHandler):
    @exeTime
    def post(self):
        path = self.request.path
        data = self.request.body
        logger.info("path of request:%s" % (path))
        logger.info("data of request:%s" % (data))
        ans_dict = dict()
        try:
            if data:
                ans_dict = sp.run(data)
                logger.info('len and keys in ans_dict: {}, {}'.format(len(ans_dict), ans_dict.keys()))
        except Exception as e:
            logger.info("this req has error: {}".format(str(e)))
        ans_str = json.dumps(ans_dict, ensure_ascii=False)
        self.write(ans_str)

application = tornado.web.Application([
    (r"/sentence_paraphrase/", SentParaHandler),
])

if __name__ == "__main__":
    myserver = HTTPServer(application)
    myserver.bind(options.port)
    myserver.start(num_processes=1)
    logger.info('sentence paraphraser server is running....')
    tornado.ioloop.IOLoop.current().start()
