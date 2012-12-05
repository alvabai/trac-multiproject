# -*- coding: utf-8 -*-
"""
Module contains some helpful functions.
"""
import os
import types

from genshi.filters import HTMLSanitizer
from genshi.input import HTML

from multiproject.core.db import admin_query


def safe_address(env, address):
    """
    Ensures the given address points to service itself
    :returns: Address or None if address is considered dangerous
    """

    if address:
        domain_name = env.config.get('multiproject', 'domain_name')
        if address.startswith("http://{0}".format(domain_name)) or address.startswith("https://{0}".format(domain_name)):
            return address
    return None


def redirect(req, toaddress=None):
    """
    Redirects user to specified address
    """
    if not req.session.has_key('goto'):
        req.session['goto'] = req.base_url + req.path_info
        req.session.save()
    if toaddress:
        req.redirect(toaddress)


def resolve_project_id(env_name):
    """
    Helper function for resolving project id based on name

    .. NOTE:: Avoid using! This one needs to be phased out.

        Use `project_id` from :class:`multiproject.common.projects.project` instead.
    """
    query = """
    SELECT project_id
    FROM projects
    WHERE environment_name = %s
    """
    row = None

    with admin_query() as cursor:
        try:
            cursor.execute(query, env_name)
            row = cursor.fetchone()
        except:
            # NOTE: this import must remain here or circular import will occur
            from multiproject.core.configuration import conf
            conf.log.exception("Failed to get project id with query: %s" % query)

    if row:
        return row[0]

    return 0


def env_id(env_name):
    """
    Helper function for getting Trac `environment_id` or `environment_key` based
    on environment name.

    .. NOTE:: Avoid using! This one needs to be phased out.

        Use `trac_environment_key` from :class:`multiproject.common.projects.project`
        instead or even better switch to `project_id` !
    """

    query = "SELECT environment_id FROM trac_environment WHERE identifier = %s"
    row = None

    with admin_query() as cursor:
        try:
            cursor.execute(query, env_name)
            row = cursor.fetchone()
        except:
            # NOTE: this import must remain here or circular import will occur
            from multiproject.core.configuration import conf
            conf.log.exception("Didn't find environment id for %s" % env_name)

    if row:
        return row[0]

    return 0


def to_web_time(datetime, show_year=True):
    day = datetime.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    if show_year:
        return datetime.strftime("%B " + str(day) + suffix + ", %Y")
    else:
        return datetime.strftime("%B " + str(day) + suffix)


def sanitize_html(input):
    """
    Sanitizes the given string or markup into text
    Example::

    >>> html = 'playnice<something>nasty<!-- javascript --></something>'
    >>> sanitize_html(html)
    'playnice'
    >>> html = '<nasty>nasty<!-- javascript --></something>'
    >>> sanitize_html(html)
    ''
    >>> html = 'plain'
    >>> sanitize_html(html)
    'plain'

    """
    if not input:
        return ''

    if type(input) in (types.StringType, types.UnicodeType, types.IntType):
        input = HTML(input)

    return str(input | HTMLSanitizer())


def format_filename(filename, max_width=None):
    if not max_width:
        return filename
    if len(filename) < max_width:
        return filename
    half_supposed = max_width / 2 - 1
    if half_supposed < 3:
        half_supposed = 2
    return '{0}...{1}'.format(filename[:half_supposed], filename[-half_supposed:])
