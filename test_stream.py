#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Testing the streaming code"""

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

parser = argparse.ArgumentParser(description='Log some streams')
parser.add_argument('-a', '--app-token', dest='app_token',
                    help='App token for your stream consumer')

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    logger.setLevel(logging.DEBUG)
    args = parser.parse_args()
    test_stream_consumer = StreamConsumer(args.app_token, 'test_stream', STREAM_OBJECT)
    test_stream_consumer.start()
