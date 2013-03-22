#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Full script used in blog post at http://h6o6.com/2013/03/using-python-and-the-nltk-to-find-haikus-in-the-public-twitter-stream

4-clause license (original "BSD License")

Copyright (c) 2013, h6o6
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. All advertising materials mentioning features or use of this software
   must display the following acknowledgement:
   This product includes software developed by the <organization>.
4. Neither the name of the <organization> nor the
   names of its contributors may be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY h6o6 ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

import argparse
import logging
import sys

from mmmercury import StreamConsumer

STREAM_OBJECT = {
    "object_types": [
        "post",
        "star",
        "user_follow",
    ],
    "type": "long_poll",
    "key": 'test_stream'
}

# natural language toolkit for syllable countin
import nltk
from nltk.corpus import cmudict

# digit detection
from curses.ascii import isdigit

ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words('english'))
NON_ENGLISH_STOPWORDS = set(nltk.corpus.stopwords.words()) - ENGLISH_STOPWORDS

def is_english(text):
    text = text.lower()
    words = set(nltk.wordpunct_tokenize(text))
    return len(words & ENGLISH_STOPWORDS) > len(words & NON_ENGLISH_STOPWORDS)

def is_haiku(text):
    import re
    text_orig = text
    text = text.lower()
    if filter(str.isdigit, str(text)):
        return False
    words = nltk.wordpunct_tokenize(re.sub('[^a-zA-Z_ ]', '',text))
    
    syl_count = 0
    word_count = 0
    haiku_line_count = 0
    lines = []
    d = cmudict.dict()
    for word in words:
        syl_count += [len(list(y for y in x if isdigit(y[-1]))) for x in
                d[word.lower()]][0]
        if haiku_line_count == 0:
            if syl_count == 5:
                lines.append(word)
                haiku_line_count += 1
        elif haiku_line_count == 1:
            if syl_count == 12:
                lines.append(word)
                haiku_line_count += 1
        else:
            if syl_count == 17:
                lines.append(word)
                haiku_line_count += 1

    if syl_count == 17:
        try:
            final_lines = []

            str_tmp = ""
            counter = 0
            for word in text_orig.split():
                str_tmp += str(word) + " "
                if lines[counter].lower() in str(word).lower():
                    final_lines.append(str_tmp.strip())
                    counter += 1
                    str_tmp = ""
            if len(str_tmp) > 0:
                final_lines.append(str_tmp.strip())
            return final_lines

        except Exception as e:
            print e
            return False
    else:
        return False

parser = argparse.ArgumentParser(description='Log some streams')
parser.add_argument('-a', '--app-token', dest='app_token',
                    help='App token for your stream consumer')
parser.add_argument('-n', '--stream-name', dest='stream_name',
                    help='Name for your stream (gets stored in redis)')


class HaikuStream(StreamConsumer):

    def on_post(self, data, meta, is_delete):
        repost = data.get('repost_of')
        if repost:
            return

        try:
            if is_english(data['text']):
                haiku_result = is_haiku(data['text'])
                if haiku_result is not False:
                    print "%s\nby %s" % (data['text'], data['user']['username'])

        except Exception:
            pass

    def on_fallback(self, data, meta, is_delete):
        pass


def main():

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    logger.setLevel(logging.INFO)
    args = parser.parse_args()
    print "Establishing stream"
    haiku_test = "Learn to Write haiku there are rules for syllables ham radio rest"
    if is_haiku(haiku_test) is not False and len(is_haiku(haiku_test)) == 3:
        print "Haiku detection is (probably) working properly"

    else:
        print "Haiku detection (probably) broken :("

    test_stream_store = HaikuStream(args.app_token, 'test_stream', STREAM_OBJECT)
    test_stream_store.start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "\n Later gator!"
