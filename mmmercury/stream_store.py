import json
import logging
import langid

from .stream_consumer import StreamConsumer
from .redis_utils import PostStore, PostActivitySet

logger = logging.getLogger(__name__)


class StreamStore(StreamConsumer):
    def __init__(self, *args, **kwargs):
        self.key_prefix = kwargs.pop('key_prefix')
        self.post_cap = kwargs.pop('post_cap', 60000)
        self.connection = kwargs.pop('connection')

        super(StreamStore, self).__init__(*args, **kwargs)

        self.post_store = PostStore(key_prefix=self.key_prefix, cap=self.post_cap, connection=self.connection)

    def on_activity(self, activity, data, user, is_delete):
        activity_store = PostActivitySet(self.key_prefix, activity, data['id'], connection=self.connection)
        user_id = user and user.get('id', None)
        if not user_id:
            return

        if is_delete:
            activity_store.srem(user_id)
            logger.info("Deleting %s on %s by %s", activity, data['id'], user_id)
        else:
            activity_store.sadd(user_id)
            logger.info("Storing %s on %s by %s", activity, data['id'], user_id)

    def on_star(self, data, meta, is_delete):
        return self.on_activity('star', data.get('post'), data.get('user'), is_delete)

    def on_post(self, data, meta, is_delete):
        score = int(data['id'])
        if is_delete:
            self.post_store.zremrangebyscore(score, score)
            logger.info("Deleting %s", score)
            return

        repost = data.get('repost_of')
        if repost:
            self.on_activity('repost', repost, data.get('user'), is_delete)
            return

        # Classify on the way in so we don't have to reclassify everytime we rank the post
        lang, conf = langid.classify(data.get('text', ''))
        conf = int(conf * 100)
        data['lang'] = lang
        data['lang_conf'] = conf

        self.post_store.add(score, json.dumps(data))
        logger.info("Storing post %s", score)
