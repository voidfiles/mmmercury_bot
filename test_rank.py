#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Testing the ranking code"""

import logging
import sys
import redis

from mmmercury.post_rank import rank_posts
from mmmercury.redis_utils import RateLimitedPoster


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    logger.setLevel(logging.DEBUG)
    connection = redis.StrictRedis(host='localhost', port=6379, db=2)
    top_posts = rank_posts(connection=connection)
    top_post_ids = []
    for post in top_posts:
        top_post_ids.append(post['id'])
        # logger.debug('%s @%s: %s', post['score'], post['user']['username'], post['text'].replace('\n', ' '))
    top_post_ids.reverse()
    item_poster = RateLimitedPoster(key_prefix='mmmercury', connection=connection)
    old_items, new_items = item_poster.add_items(top_post_ids)
    next_post_id_to_publish = item_poster.rpop()
    logger.info("Post Queue Length: %s Published: %s New posts: %s Next to publish: %s", len(item_poster.unpublished), len(item_poster.published), len(new_items), next_post_id_to_publish)
