#!/usr/bin/env python
# coding: utf-8

"""use PyPi's sh package to wrap git commands
"""

from sh import git
from sh import svn
from sh import hg

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
    # Git 1.7 requires that with the first push remote and branch are specified.
    val = git("push", "-v", "origin", "master")
    if val.exit_code != 0:
        raise ValueError ("Commit failed with status ", val)
    else:
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
    try:
        current = os.getcwd()
    except OSError:
        current = None
    os.chdir(dir)
    return current

def git_ls_files():
    """List repository files in current dir.""" 
    val = git("ls-files")
    return val

def svn_checkout(remote, local):
    # Note that for Mac, this requires a more modern version of svn to be
    # installed than comes with Mac os 10.8. At least SVN 1.7.9 with Openssl
    # 1.0.1e works.
    val = svn("co", "--trust-server-cert", "--non-interactive", remote, local)
    if val.exit_code != 0:
        raise ValueError ("Checkout failed with status ", val)
    else:
        return val

def svn_add(fname):
    val = svn("add", fname)
    if val.exit_code != 0:
        raise ValueError("svn add failed with status ", val)
    else:
        return val

def svn_commit(user, pwd, msg):
    val = svn("commit", "--username", user, "--password", pwd, "--no-auth-cache", "-m", msg)
    if val.exit_code != 0:
        raise ValueError ("Commit failed with status ", val)
    else:
        return val

def hg_clone(remote, local):
    val = hg("clone", "--insecure", remote, local)
    if val.exit_code != 0:
        raise ValueError ("Clone failed with status ", val)
    else:
        return val

def hg_commit(username, filename="", msg=""):
    val = hg.commit("-A", "-m", msg, filename)
    if val.exit_code != 0:
        raise ValueError ("Commit failed with status ", val)
    else:
        return val

def hg_push(url):
    """Push commits to repository, provided that we are already in the repo.
    """
    val = hg("push", "--insecure", url)
    if val.exit_code != 0:
        raise ValueError ("Commit failed with status ", val)
    else:
        return val


if __name__ == "__main__":
    print "not impelmented"
    pass



# vim: sw=4

