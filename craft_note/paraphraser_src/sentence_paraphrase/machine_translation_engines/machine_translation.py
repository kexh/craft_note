# -*- coding: utf-8 -*-

import json
import requests
from paraphraser_conf import re_run
from common.logger import logger

class Translation(object):
    def req_get(self, url, req_dict, **kw):
        resp = {}
        for i in range(re_run):
            try:
                req = requests.get(url=url, params=json.dumps(req_dict))
                resp = json.loads(req.content)
                break
            except Exception as e:
                logger.info('error req get(may re_run): {}'.format(str(e)))
        return resp


