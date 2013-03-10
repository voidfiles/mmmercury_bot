#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Testing the ranking code"""

import logging
import sys
import redis

from mmmercury.post_rank import rank_posts


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    logger.setLevel(logging.DEBUG)
    connection = redis.StrictRedis(host='localhost', port=6379, db=2)
    top_posts = rank_posts(connection=connection)
    for post in top_posts:
        print '%s @%s: %s' % (post['score'], post['user']['username'], post['text'].replace('\n', ' '))