#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Testing the streaming code"""

import argparse
import logging
import sys
import redis

from mmmercury import StreamStore

STREAM_OBJECT = {
    "object_types": [
        "post",
        "star",
        "user_follow",
    ],
    "type": "long_poll",
    "key": 'test_stream'
}

parser = argparse.ArgumentParser(description='Log some streams')
parser.add_argument('-a', '--app-token', dest='app_token',
                    help='App token for your stream consumer')
parser.add_argument('-n', '--stream-name', dest='stream_name',
                    help='Name for your stream (gets stored in redis)')


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    logger.setLevel(logging.DEBUG)
    args = parser.parse_args()
    connection = redis.StrictRedis(host='localhost', port=6379, db=2)
    test_stream_store = StreamStore(args.app_token, 'test_stream', STREAM_OBJECT,
                                    key_prefix=args.stream_name, connection=connection)
    test_stream_store.start()
