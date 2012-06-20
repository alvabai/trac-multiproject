# -*- coding: utf-8 -*-
"""
Contents of this module
"""
from subprocess import PIPE, Popen, call
import sys
import os

from fabric.api import task, cd, local, lcd, settings, show, hide, warn

from fablib.api import local, get_files, logger


@task
def remove_unused_images(dirpath, extensions='*.png', cmd=''):
    """
    List/remove unused images

    :param dirpath: Directory where to search for unused images
    :param extensions: Extensions to include in search. Example: "*.png", "*.png,*.gif"
    :param cmd: Command to execute on unsed images. For example: "git rm", "rm"
                The file path is appended in the end of the command. By default, just prints the image path

    Example execution::

        fab devel.remove_unused_images:"themes/default/",cmd="git rm"

    """
    dirpath = os.path.abspath(dirpath or os.path.curdir)
    logger.info('Looking for unused images: %s' % dirpath)

    # Iterate images
    for imagepath in get_files(dirpath, extensions, recursive=True):
        logger.debug('Processing image: %s' % imagepath)
        image = os.path.basename(imagepath)

        with settings(hide('running', 'stderr'), warn_only=True):
            # Run inside the dirpath
            with lcd(dirpath):
                # Check if image can be found from source files
                findcmd = 'grin "%s"' % image
                search = local(findcmd, capture=True)

                # If output does not contain image, then it is unused
                if not search.stdout:
                    if cmd:
                        rmcmd = '%s %s' % (cmd, imagepath)
                        logger.info('Executing command: %s' % rmcmd)
                        local(rmcmd)
                    else:
                        logger.info('Unsed image: %s' % imagepath)
