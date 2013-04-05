#!/usr/bin/env python
# coding: utf-8

def get_session_cookie(cookies, key="trac"):
    """Return a list of cookies and their values having key in name.

    >>> get_session_cookie(['foo_session=a0jkas0, expires=Thu, 04-Jul-2013 04:52:37 GMT; Path=/home', 'foo_form=4de338; bar=34asf;'], key="foo")
    'foo_session=a0jkas0; foo_form=4de338'

    >>> get_session_cookie(['foo_session=abc, expires=Thu, 04-Jul-2013 04:52:37 GMT; Path=/home'], key="foo")
    'foo_session=abc'

    """

    s_cookies = [parse_cookie(c, key) for c in cookies]
    return "; ".join(s_cookies)


def parse_cookie(cookie, sub="session"):
    """Return cookie containing searched substring and its value.

    >>> parse_cookie('foo_session=890az; expires=Thu, 04-Jul-2013 04:52:37 GMT; Path=/home')
    'foo_session=890az'

    >>> parse_cookie('foo_session=890az; foo_auth=4de33; expires=Sun, 07 Apr 2013 08:04:33; Path=/', sub="auth")
    'foo_auth=4de33'
    """

    session_strings = [x.rstrip(' ,;') for x in cookie.split() if sub in x]

    # we don't expect more than one session value in one cookie
    assert(len(session_strings) == 1) 
    return session_strings.pop()




if __name__ == "__main__":
    import doctest
    doctest.testmod()

# vim: sw=4

