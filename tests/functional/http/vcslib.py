#!/usr/bin/env python
# coding: utf-8

"""use PyPi's sh package to wrap git commands
"""

from sh import git
import os

def git_clone(remote, local):
    # setting environment variable GIT_SSL_NO_VERIFY=true is needed to enable
    # cloning from unverified repository.
    val = git("clone", remote, local)
    if val.exit_code != 0:
        raise ValueError ("Commit failed with status ", val)
    else:
        return val

def git_push():
    """Push commits to repository, provided that we are already in the repo.
    """
    val = git("push")
    return val

def git_commit(filename="", msg=""):
    val = git.commit("-m", msg, filename)
    if val.exit_code != 0:
        raise ValueError ("Commit failed with status ", val)
    else:
        return val

def git_add(fname):
    val = git("add", fname)
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

