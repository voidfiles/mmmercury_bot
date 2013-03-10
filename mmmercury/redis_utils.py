from redisco.containers import SortedSet, Set


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
