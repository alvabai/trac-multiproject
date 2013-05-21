#!/usr/bin/env python
# coding: utf-8

"""use PyPi's sh package to wrap git commands
"""

from sh import git
import os

def git_clone(remote, local):
    val = git("clone", remote, local)
    return val

def git_push(url, repo):
    """Push commits to repository, provided that we are already in the repo.
    """
    val = git("push")
    return val

def git_commit():
    val = git("commit")
    return val

def git_add():
    val = git("add")
    return val

def cd(dir):
    """Cd to dir and return previous one."""
    current = os.getcwd()
    os.chdir(dir)
    return current

def git_ls_files():
    """List repository files in current dir.""" 
    val = git("ls-files")
    return val

if __name__ == "__main__":
    print "not impelmented"
    pass



# vim: sw=4

