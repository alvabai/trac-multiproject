# -*- coding: utf-8 -*-
"""
Module for mapping project identifier into trac environment key and data,
the multiproject way.
"""
import hashlib

from trac.core import TracError

from multiproject.core.db import admin_query
from multiproject.core.configuration import Configuration
conf = Configuration.instance()

class TracEnvironment(object):
    """
    This is a class that represents a trac environment, with environment id and project identifier
    pair.
    """
    def __init__(self, params):
        self.params = params

    def __getattr__(self, key):
        """
        Implements a dict like accessor for key. Throws exception if key is missing.
        """
        return self.params[key]

    @staticmethod
    def read(identifier):
        """
        Static method for reading trac environment from database. Returns an instance of a Trac project
        environment, or raises TracError if database read fails (or environment is not found).
        The data is also saved to memcache daemon if it's in use.

        :param identifier: The project identifier in uri, that's tried to be read.
        """
        row = TracEnvironment._try_from_cache(identifier)
        if not row:
            with admin_query() as cursor:
                try:
                    query = "SELECT environment_id, identifier FROM trac_environment WHERE identifier = %s"
                    cursor.execute(query, identifier)
                    row = cursor.fetchone()
                    TracEnvironment._set_into_cache(identifier, row)
                except:
                    conf.log.exception("Failed finding trac environment for %s" % identifier)
                    pass

        if not row:
            raise TracError('Environment %s not found' % identifier)
        params = {'environment_id': row[0], 'identifier': row[1]}
        return TracEnvironment(params)

    @staticmethod
    def _try_from_cache(identifier):
        """
        Static, private method for reading the TracEnvironment data from memcached. Returns just
        plain data, as it would be fetch from database, not the instance.

        :param identifier: The project environment identifier
        """
        mc = conf.getMemcachedInstance()
        key = TracEnvironment._mc_key(identifier)
        return mc.get(key)

    @staticmethod
    def _set_into_cache(identifier, row):
        """"
        Static, private method for setting the environment data into memcache daemon... as it is got
        from database.

        :param identifier: The project environment identifier
        :param row: The data for project in an array, environment identifier on first element, project
                    identifier on second element.
        """
        mc = conf.getMemcachedInstance()
        key = TracEnvironment._mc_key(identifier)
        return mc.set(key, row, 60 * 5)

    @staticmethod
    def _mc_key(identifier):
        """
        Return a memcached capable key for the environment

        :param identifier: The environment identifier
        """
        key = identifier.encode('utf-8')

        m = hashlib.sha256()
        m.update('tracenv:')
        m.update(key)

        return m.hexdigest()

    def __str__(self):
        return "<TracEnvironment (%s)>" % self.params
