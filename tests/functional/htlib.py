#!/usr/bin/env python
# coding: utf-8

def get_session_cookies(cookies, key="trac"):
    """Return a string of cookies and their values having key in name.

    >>> get_session_cookies(['foo_session=a0jkas0, expires=Thu, 04-Jul-2013 04:52:37 GMT; Path=/home', 'foo_form=4de338; bar=34asf;'], key="foo")
    'foo_session=a0jkas0; foo_form=4de338'

    >>> get_session_cookies(['foo_form_token=d984; Path=/home', 'foo_session=bb64312be8e55f0a10a49c10; expires=Thu, 04-Jul-2013 15:08:14 GMT; Path=/home'], key="form")
    'foo_form_token=d984'

    >>> get_session_cookies(['foo_session=abc, expires=Thu, 04-Jul-2013 04:52:37 GMT; Path=/home'], key="foo")
    'foo_session=abc'

    """

    if not type(cookies) == list:
        cookies = [cookies]
    assert(type(cookies) == list),  "cookies is not a list"
    s_cookies = [parse_cookie(c, key) for c in cookies if key in c]
    return "; ".join(s_cookies)


def headers_to_dict(cookies, key="trac"):
    """Return a dict with cookies but strip all cookie attributes.

    >>> headers_to_dict('foo_session=890az; expires=Thu, 04-Jul-2013 04:52:37 GMT; Path=/home', key="foo")
    {'foo_session': '890az'}

    >>> headers_to_dict(['foo_session=890az', 'foo_auth=4de33; Path=/'], key="foo")
    {'foo_session': '890az', 'foo_auth': '4de33'}
    """

    if not type(cookies) == list:
        cookies = [cookies]

    def ck_to_dict(ck_string):
        """ Go trough the cookies, and leave only strings having 'key' as a
        substring.  Then, trusting that the strings look like 'key=value', create
        a dictionary from them and return it.
        """
        ck_list = [x.strip() for x in ck_string.split('; ') if key in x]
        ck_list = [tuple(x.split('=')) for x in ck_list]
        return dict(ck_list)

    c_dict = {}
    for ck in cookies:
        c_dict.update(ck_to_dict(ck))

    return c_dict


def update_dictionary(base, updates):
    """Update dictionary 'base' with keys and values from dictionary 'updates'."""
    return base.update(updates)


def get_cookie_header(data):
    """ Parse dict having cookies and return them in a string suitable for
    sending in HTTP request.
    """
    assert(type(data) == dict)
    return "; ".join(["%s=%s" % (k,v) for k,v in data.items()])


def parse_cookie(cookie, sub="session"):
    """Return cookie containing searched substring and its value.

    >>> parse_cookie('foo_session=890az; expires=Thu, 04-Jul-2013 04:52:37 GMT; Path=/home')
    'foo_session=890az'

    >>> parse_cookie('foo_session=890az; foo_auth=4de33; foo_form_token=1234; expires=Sun, 07 Apr 2013 08:04:33; Path=/', sub="auth")
    'foo_auth=4de33'

    >>> parse_cookie('foo_session=890az; foo_auth=4de33; foo_form_token=1234; expires=Sun, 07 Apr 2013 08:04:33; Path=/', sub="form")
    'foo_form_token=1234'
    """

    assert(type(cookie) == str) , "cookie is not a string but a " % type (cookie)
    session_strings = [x.rstrip(' ,;') for x in cookie.split() if sub in x]

    # we don't expect more than one session value in one cookie
    assert(len(session_strings) == 1), "more than one matching value"
    return session_strings.pop()



if __name__ == "__main__":
    import doctest
    doctest.testmod()



# vim: sw=4

