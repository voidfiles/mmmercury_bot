import pytz
import json
from iso8601 import parse_date
import itertools
from datetime import datetime
from collections import Counter
from math import log

from .stream_store import PostStore
from .redis_utils import PostActivitySet

# Ranking Utilities
GRAVITY = 1.8


def balance(num, log_factor=10):
    return log(max(abs(int(num)), 1), log_factor)


def delta_from_now(date):
    now = datetime.now(pytz.utc)
    return now - parse_date(date)


def date_in_days(date):
    """How long ago in days"""
    delta = delta_from_now(date)
    return (delta.days) + delta.seconds / 86400


def date_in_hours(date):
    """How long ago in hours"""
    delta = delta_from_now(date)
    return (delta.days * 24) + delta.seconds / (60 * 60)


def date_in_day_parts(date, hours=4):
    """ If days are to big, and hours are to small """
    delta = delta_from_now(date)
    return (delta.days * 4) + delta.seconds / (4 * 60 * 60)


# Follows the HN model of votes and decay
def hn_weight(post, add=2, gravity=GRAVITY):
    return pow((date_in_days(post['created_at']) + add), gravity)


def hn_weight_hours(post, add=2, gravity=GRAVITY):
    return pow((date_in_hours(post['created_at']) + add), gravity)


def hn_weight_day_parts(post, add=2, gravity=GRAVITY):
    return pow((date_in_day_parts(post['created_at']) + add), gravity)


# various filters to take things out of consideration
def lang_filter(lang='en', min_conf=85):
    def lf(post):
        plang = post.get('lang')
        lang_conf = post.get('lang_conf')
        if not lang or not lang_conf:
            return post

        if lang_conf < min_conf:
            return post

        if plang == lang and lang_conf > min_conf:
            return post

        return False

    return lf

english_lang_filter = lang_filter()


def at_mention_filter(post):
    mentions = post.get('entities', {}).get('mentions', [])
    if not mentions:
        return post

    if len(mentions) < 4 and mentions[0]['pos'] != 0:
        return post

    return False


# post scoring functions

def post_activity_score(post, key_prefix, connection):
    star_activity = PostActivitySet(key_prefix, 'star', post['id'], connection=connection)
    repost_activity = PostActivitySet(key_prefix, 'repost', post['id'], connection=connection)

    unique_user_ids = star_activity.smembers() | repost_activity.smembers()

    return len(unique_user_ids)

POST_CAP = 60000
POST_STORE_PREFIX = 'mmmercury'
DEFAULT_MAPS = (json.loads,)
DEFAULT_FILTERS = (english_lang_filter, at_mention_filter)
MAX_RANK = 100
DEFAULT_SCORE_FUNC = post_activity_score
DEFAULT_WEIGHT_FUNC = hn_weight


def rank_posts(key_prefix=POST_STORE_PREFIX, max_store=MAX_RANK, filters=DEFAULT_FILTERS, maps=DEFAULT_MAPS,
               score_func=DEFAULT_SCORE_FUNC, weight_func=DEFAULT_WEIGHT_FUNC, connection=None):
    posts = PostStore(key_prefix=POST_STORE_PREFIX, cap=POST_CAP, connection=connection)

    for post_map in maps:
        posts = itertools.imap(post_map, posts)

    for post_filter in filters:
        posts = itertools.ifilter(post_filter, posts)

    post_scores = Counter()
    for post in posts:
        score = score_func(post, key_prefix, connection)
        weight = weight_func(post)

        post_scores[post['id']] = score / weight

    posts = PostStore(key_prefix=POST_STORE_PREFIX, cap=POST_CAP, connection=connection)

    top_post_scores = post_scores.most_common(max_store)
    top_posts = []
    for post_id, score in top_post_scores:
        post = posts.eq(post_id)
        post = post and json.loads(post[0])
        if post:
            post['score'] = score
            top_posts += [post]

    return sorted(top_posts, key=lambda x: x['score'])
