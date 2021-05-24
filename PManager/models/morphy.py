# -*- coding:utf-8 -*-
__author__ = 'Gvammer'
from pymorphy.django_conf import default_morph as morph
from pymorphy.contrib import tokenizers
import re

class trackMorphy():
    text = u''  # текст для обработки
    tags = []  # массив тэгов (каждый тэг является объектом Tags)
    allowWordClasses = [u'С', u'ИНФИНИТИВ', u'Г', u'П']

    # parse text and returns array of tags
    def parseTags(self, text=u''):

        if text:
            self.text = text

        tags = {}
        if len(self.text) > 0:
            for word in tokenizers.extract_words(self.text):
                wordUpper = unicode(word).upper()
                if re.match('([A-z\-\._]+)', wordUpper): #for english words
                    if wordUpper in tags:
                        tags[wordUpper]['weight'] += 1
                    else:
                        tags[wordUpper] = {
                            'class': u'С',
                            'weight': 1,
                            'norm': wordUpper
                        }
                else:
                    gramInfo = morph.get_graminfo(wordUpper)
                    if len(gramInfo) > 0:
                        gramInfo = gramInfo[0]

                        if gramInfo['class'] in self.allowWordClasses:
                            normolizeWord = gramInfo.get("norm", u'')
                            if len(normolizeWord) > 2 and len(normolizeWord) < 50:
                                if normolizeWord in tags:
                                    tags[normolizeWord]['weight'] += 1
                                else:
                                    gramInfo['weight'] = 1
                                    tags[normolizeWord] = gramInfo

        return tags