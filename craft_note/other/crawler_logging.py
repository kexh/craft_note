# -*- coding: utf-8 -*-
'''
@author: kexh
@create: 2017/08/16
@update: 2017/08/30
'''

import logging
from logging.handlers import RotatingFileHandler

class SecLogger(object):
    def __init__(self):
        pass
    def sec(self, thread_name, filename):
        formatter = logging.Formatter("_'%(filename)s'_line:%(lineno)s_%(asctime)-2s]%(levelname)s: %(message)s")
        logger = logging.getLogger(thread_name)
        logger.setLevel(logging.DEBUG)
        rt = RotatingFileHandler(filename, maxBytes=1024*521,backupCount=300)
        rt.setFormatter(formatter)
        formatter._fmt  = '[thread_name:' + thread_name + formatter._fmt
        logger.addHandler(rt)
        return logger

if __name__ == '__main__':
    log_file = r'F:/w_logging.txt'
    seclogger_main = SecLogger()
    logger_main = seclogger_main.sec('MainLog', log_file)
    print('main running...')
    logger_main.info('main running...')
    # [thread_name: MainLog_'weather_crawl_sync_logging.py'_line: 28_2017-08-30 10:19:29,812]INFO: main running...