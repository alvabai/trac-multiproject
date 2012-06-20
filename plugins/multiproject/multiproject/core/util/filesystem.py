# -*- coding: utf-8 -*-
"""
Module contains a set of handy filesystem related tools and functions, used by Multiproject plugin:

- rmtree: Recursive delete with error handler
- safe_path: Secure path join

"""
import logging
import shutil
import os
import stat

from trac.core import TracError


def rmtree(path):
    """
    Customized version of ``shutil.rmtree`` to handle corner cases like:

    - If file or directory has ownership but not write permissions, try setting it first

    :param str path: Directory to delete
    """
    orgpath = path

    def rm_handler(func, path, exc_info):
        # Read/write/execute permissions
        mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR

        # Set write permission to all files and folders
        for root, dirs, files in os.walk(orgpath):
            for entry in dirs:
                os.chmod(os.path.join(root, entry), mode)
            for entry in files:
                os.chmod(os.path.join(root, entry), mode)

        # Set mode to root path and problematic path as well
        os.chmod(path, mode)
        os.chmod(orgpath, mode)

        # Try again
        func(path)

    return shutil.rmtree(path, onerror=rm_handler)

def safe_path(*path_parts):
    """
    Joins the path elements similar to ``os.path.join`` but in more secure manner

    Check the parameters for not containing '..' or '/'.
    This is because os.path.join is used, which ignores previous parts if one part begins with '/'.
    If some args are empty, they are not used.
    Returns a string like '/', '/folder', '/folder/file.txt'

    >>> filesystem.safe_path('path', 'foo')
    'path/foo'
    >>> filesystem.safe_path('/path', 'foo')
    '/path/foo'
    >>> filesystem.safe_path('/path', '/foo')
    <TracError..>
    >>> filesystem.safe_path('/path', '../foo')
    <TracError..>

    :returns: Filesystem path, joined securely from given parts
    """
    res_path_parts = []
    for index, path_part in enumerate(path_parts):
        # Skip empty elements
        if not path_part:
            continue

        # Normalize path from multiple slashes
        path_part = os.path.normpath(path_part)

        # No .. are allowed
        if '..' in path_part:
            logging.warning('Invalid file path. Path arguments: {0}'.format(path_parts))
            raise TracError('Error in filename or path')

        # Starting slash is only allowed for first element
        if not index == 0 and path_part.startswith('/'):
            logging.warning('Invalid file path. Path arguments: {0}'.format(path_parts))
            raise TracError('Error in filename or path')

        res_path_parts.append(path_part)

    return os.path.join(*res_path_parts) if res_path_parts else '/'


