#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Testing the streaming code on heroku"""

import logging
import sys
import os
import redis

from mmmercury import StreamConsumer

STREAM_OBJECT = {
    "object_types": [
        "post",
        "star",
        "user_follow",
    ],
    "type": "long_poll",
    "key": 'test_stream_heroku'
}

logger = logging.getLogger(__name__)


class StreamRepost(StreamConsumer):
    def on_post(self, data, meta, is_delete):
        logger.info("Storing post %s", data['id'])


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    logger.setLevel(logging.INFO)
    app_token = os.getenv('APP_TOKEN')
    test_stream_store = StreamRepost(app_token, 'test_stream', STREAM_OBJECT)
    test_stream_store.start()
