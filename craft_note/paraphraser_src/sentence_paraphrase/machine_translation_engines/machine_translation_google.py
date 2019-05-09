# /usr/bin/env python
# coding=utf8

from googletrans import Translator
from paraphraser_conf import google_trans_url

class SiteTranslator(object):
    def __init__(self):
        self.translator = Translator(service_urls=[google_trans_url])

    def get_translation(self, sent, src, dest):
        text = self.translator.translate(text=sent, src=src, dest=dest).text
        return text

    def translate(self, sent, src, tgt):
        return self.get_translation(sent=sent,src=src, dest=tgt)


