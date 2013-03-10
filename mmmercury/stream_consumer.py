import json
import logging
import requests
import time

from adn_request import AdnClient

logger = logging.getLogger(__name__)


class StreamConsumer(object):

    def __init__(self, app_access_token, stream_name, stream_conf):
        self.app_access_token = app_access_token
        self.stream_name = stream_name
        self.stream_conf = stream_conf
        self.adn_client = AdnClient(access_token=app_access_token)

    def start(self):
        response = self.adn_client.streams(params={'key': self.stream_name})
        if not response['data']:  # If we don't have any streams make one
            logger.info('Creating a stream object: %s', self.stream_conf)
            response = self.adn_client.streams(method="POST", params=json.dumps(self.stream_conf))
            stream_endpoint = response['data']['endpoint']
        else:
            stream_endpoint = response['data'][0]['endpoint']

        logger.info("Starting to fetch stream: %s", stream_endpoint)

        while True:
            r = requests.get(stream_endpoint, stream=True, timeout=600)
            if r.ok:
                for line in r.iter_lines(chunk_size=1):
                    if not line:
                        continue

                    blob = json.loads(line)

                    if not blob.get('data'):
                        continue

                    is_delete = blob['meta'].get('is_deleted')
                    message_type = blob['meta'].get('type')
                    method_name = 'on_%s' % (message_type,)
                    func = getattr(self, method_name, self.on_fallback)

                    func(blob['data'], blob['meta'], is_delete)
            else:
                logger.warning('Failed to connect to stream endpoint')

            logger.warning("Waiting one second before retrying")
            time.sleep(1)

    def on_fallback(self, data, meta, is_delete):
        logger.info('Fallback blob processor Message Type: %s Timestamp: %s', meta['type'], meta['timestamp'])
