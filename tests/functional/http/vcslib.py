#!/usr/bin/env python
# coding: utf-8

"""use PyPi's sh package to wrap git commands
"""

from sh import git
import os

def git_clone(url, repo):
    val = git("clone", url, repo)
    return val

def git_push(url, repo):
    """Push commits to repository, provided that we are already in the repo.
    """
    val = git("push")
    return val


if __name__ == "__main__":
    print "not impelmented"
    pass



# vim: sw=4

