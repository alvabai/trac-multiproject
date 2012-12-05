"""
Implements memoization type of caching with memcached
"""
from functools import wraps
from hashlib import sha256
import itertools

from multiproject.core.configuration import Configuration


class memcached(object):

    """
    Memcached based function and method memoization.

    Simplest usage::

        @memcached()
        def get_character_class(name):
            return random.choice(['wizard', 'orc', 'dwarf'])

    This will return same value for same ``name`` during cache
    duration (default is 5 minutes).

    The decorator will use construct memcached key from all function
    arguments, often this is not wanted as there may be other arguments
    that are not relevant for the cache.

    Specify key argument::

        @memcached(key_arg='name')
        def get_character_class(name, gender, strength, intellect):
            return random.choice(['wizard', 'orc', 'dwarf'])

    Multiple arguments with custom timeout::

        @memcached(key_args=['name', 'gender'], timeout=60)
        def get_character_class(name, gender, strength, intellect):
            return random.choice(['wizard', 'orc', 'dwarf'])

    Clear item from cache manually::

        @memcached(key_args=['name', 'gender'], timeout=60)
        def get_character_class(name, gender, strength, intellect):
            return random.choice(['wizard', 'orc', 'dwarf'])

        def something():
            get_character_class('foobar')
            get_character_class('ipsum')

            get_character_class.clear_memcached(name='foobar')

    Note that you will need to give the ``clear_memcached`` the argument name
    used in method signature, even if it was not kwarg originally. This is because
    argument name is used in key.

    Example::

        @memcached()
        def get_intellect(name):
            return random.intval(1, 100)

        def something():
            get_intellect('foobar')
            get_intellect('lorem')
            get_intellect('ipsum')

            get_intellect.clear_memcached(name='foobar')

    The decorator supports utilizing class attributes in key construction.

    Example::

        class Storage(object):
            def __init__(self, id):
                self.id = id

            @memcached(key_attr='id')
            def user(self, name):
                return random.choice(['Kyoma Hooin', 'John Titor'])


    In this case the clearing will need to pass the attribute name and value as well.

    Example::

        def something():
            store = Storage(333)
            store.user('foobar')
            store.clear_memcached(name='foobar', id=333)

    """

    ignored_argnames = ('self', 'cls', 'klass')

    def __init__(self, key_arg=None, key_args=None, key_attr=None, key_attrs=None, timeout=0):
        """
        :param str key_arg: Single argument name to be used in memcached key construction
        :param list key_args: List of key name arguments
        :param key_attr: If used within class, use class attribute as part of the key construction
        :param key_attrs: List of class attributes (see ``key_attr``)
        :param timeout: Specify cache duration in seconds, zero (default) means forever
        """
        if key_args and key_arg:
            raise ValueError('key_arg and key_args are mutually exclusive')
        if key_attr and key_attrs:
            raise ValueError('key_attr and key_attrs are mutually exclusive')

        self.timeout = timeout
        self.key_args = []
        self.key_attrs = []
        self.mc = Configuration.instance().getMemcachedInstance()
        if key_args:
            if not isinstance(key_args, list):
                raise ValueError('key_args must be a list')
            self.key_args.extend(key_args)
        if key_arg:
            self.key_args.append(key_arg)
        if key_attrs:
            if not isinstance(key_attrs, list):
                raise ValueError('key_attrs must be a list')
            self.key_attrs.extend(key_attrs)
        if key_attr:
            self.key_attrs.append(key_attr)

    def __call__(self, fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):

            uself = None
            arg_values = {}
            arg_names = fn.func_code.co_varnames[:fn.func_code.co_argcount]
            for name, value in itertools.chain(itertools.izip(arg_names, args), kwargs.iteritems()):
                if name == 'self':
                    uself = value
                if name in self.ignored_argnames:
                    continue
                arg_values[name] = value

            # no key_arg(s) given, use all arguments
            if not self.key_args:
                self.key_args.extend(arg_values.keys())

            # construct unique key from function name and given key_arg(s)
            key = fn.__name__

            # we need temporary dict for data, so we can iterate it sorted
            keys = {}
            for arg in self.key_args:
                keys[arg] = ';%s=%s' % (arg, arg_values[arg])
            for attr in self.key_attrs:
                keys[attr] = ';%s=%s' % (attr, getattr(uself, attr))
            for part_name, value in sorted(keys.items()):
                key += value

            # hash key so that the function values do not cause problems with
            # memcached key constraints
            key = sha256(key).hexdigest()

            cached_value = self.mc.get(key)
            if cached_value is not None:
                return cached_value

            # call original function and cache the result
            output = fn(*args, **kwargs)
            self.mc.set(key, output, self.timeout)
            return output

        # add invalidate function
        wrapped.clear_memcached = _clear_memcached(fn)
        return wrapped


class _clear_memcached(object):

    def __init__(self, fn):
        self.fn = fn
        self.mc = Configuration.instance().getMemcachedInstance()

    def __call__(self, **kwargs):

        key = self.fn.__name__
        for arg_name, value in sorted(kwargs.iteritems()):
            key += ';%s=%s' % (arg_name, value)

        key = sha256(key).hexdigest()

        self.mc.delete(key)
