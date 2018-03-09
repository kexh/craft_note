# /usr/bin/env python
# coding=utf8

import nltk
import json
import collections
import urllib2
import numpy
import requests
import traceback
from nltk.translate.bleu_score import SmoothingFunction
from paraphraser_conf import nlu_url, exeTime
from common.logger import logger

# 此脚本未改好，暂不传。