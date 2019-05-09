# -*- coding:utf-8 -*-
from __future__ import unicode_literals
'''
@author: kexh
@update: 2017/09/27
'''

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import json
import tornado.web
from tornado.options import define, options
from tornado.httpserver import HTTPServer
from common.logger import logger
from backstage_configuration.conf_op import scripts_api
from backstage_configuration_config import *

# usage: python backstage_configuration_service.py --port=8881

define('debug', default=True, help='enable debug mode')
define('server', default=servers_dict["backstage_configuration_entrance"][0], help='server')
define('port', default=int(servers_dict["backstage_configuration_entrance"][1]), help='port')
options.parse_command_line()
logger.info("begin -> {}:{}".format(options.server, options.port))

class ConfHandler(tornado.web.RequestHandler):
    def post(self):
        path = self.request.path
        data = self.request.body
        logger.info("path of request:%s" % (path))
        logger.info("data of request:%s" % (data))
        ans_dict = dict(code=4000, code_description="", data={})
        try:
            if data:
                target_server = json.loads(data).get("target_server", "bg_conf_center")
                if path in scripts_dict.keys():
                    # print("[bg_conf_center]target_server: {}, path: {}".format(target_server, path))
                    logger.info("[bg_conf_center]target_server: {}, path: {}".format(target_server, path))
                    ans_dict = scripts_api(target_server, path, data)###
                else:
                    ans_dict["code_description"] = "Unknown error: target_server value error."
                logger.info("return body:{}".format(ans_dict))
        except Exception as e:
            logger.info(e)
            ans_dict["code_description"] = "Unknown error: "+str(e)
        ans_str = json.dumps(ans_dict, ensure_ascii=False)

        self.write(ans_str)


application = tornado.web.Application([
    (r"/configure/save/", ConfHandler),
    (r"/configure/getlist/", ConfHandler),
    (r"/configure/getdetail/", ConfHandler),
    (r"/configure/test/", ConfHandler),
])


if __name__ == "__main__":
    myserver = HTTPServer(application)
    myserver.bind(options.port)
    myserver.start(num_processes=1)
    logger.info('backstage configuration server is running....')
    tornado.ioloop.IOLoop.current().start()
