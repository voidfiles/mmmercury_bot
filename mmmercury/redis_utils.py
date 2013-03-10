from redisco.containers import SortedSet, Set, List


class CappedSortedSet(SortedSet):

    def __init__(self, cap, key, connection=None):
        self.cap = cap
        return super(CappedSortedSet, self).__init__(key, connection)

    def add(self, *args, **kwargs):
        value = super(CappedSortedSet, self).add(*args, **kwargs)
        set_length = len(self)
        if set_length > self.cap:
            delete_len = set_length - self.cap
            self.zremrangebyrank(0, delete_len - 1)
        return value


class PostStore(CappedSortedSet):
    key = 'posts'
    cap = 60000

    def __init__(self, *args, **kwargs):
        key_prefix = kwargs.pop('key_prefix', '')
        kwargs['key'] = '%s:%s' % (key_prefix, self.key)
        kwargs['cap'] = kwargs.get('cap', self.cap)
        super(PostStore, self).__init__(*args, **kwargs)


class PostActivitySet(Set):

    def __init__(self, prefix, activity, post_id, connection):
        key = '%s:activity:post:%s:%s' % (prefix, activity, post_id)
        return super(PostActivitySet, self).__init__(key, connection)


class RateLimitedPoster(object):

    def __init__(self, key_prefix, unpublish_queue='unpublished', published_queue='published', connection=None):
        self.unpublished = List('%s:%s' % (key_prefix, unpublish_queue), connection)
        self.published = List('%s:%s' % (key_prefix, published_queue), connection)

    def add_items(self, items):
        old_items = []
        new_items = []
        for item in items:
            if item in self.published or item in self.unpublished:
                old_items.append(item)
            else:
                self.unpublished.lpush(item)
                new_items.append(item)

        return (old_items, new_items)

    def rpop(self):
        next_item = self.unpublished.rpop()
        if next_item:
            self.published.lpush(next_item)

        return next_item
