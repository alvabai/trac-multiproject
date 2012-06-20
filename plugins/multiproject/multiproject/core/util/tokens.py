# -*- coding: utf-8 -*-
"""
Module contains tools and classes for generating tokens.
"""
import hashlib


class SaltedToken(object):
    """
    Helper class for generating and checking the token.
    Example usage:

    >>> stoken = SaltedToken(salt='aijh29945+245ds%cee2erwgr3', 'foo')
    >>> print stoken
    '6a5cecd7e833ab9eeab8add26edfc509e6f0c63a'
    >>> stoken == '6a5cecd7e833ab9eeab8add26edfc509e6f0c63a'
    True
    >>> stoken == 'aetewce7e833ab9eeab8add26edfc50afdeaabba'
    False
    >>> stoken == SaltedToken(salt='aijh29945+245ds%cee2erwgr3', 'foo')
    True

    """
    def __init__(self, salt, *parts):
        self.salt = salt
        self.key = self.generate(*parts)

    def __cmp__(self, other):
        """
        Implements the comparison
        :returns: 0 if equal, otherwise 1
        """
        return 0 if self.key == str(other) else 1

    def __str__(self):
        """
        :returns: Generated token in a string
        """
        return self.key

    def generate(self, *parts):
        """
        Generates new token from given parts
        and stores the value in ``Token.key``
        """
        tokenss = [str(tok) for tok in ([self.salt] + list(parts))]
        self.key = hashlib.sha1(''.join(tokenss)).hexdigest()
        return self.key

