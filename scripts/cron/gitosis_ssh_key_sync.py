#!/usr/bin/env python
from subprocess import *
import os

# Read repo and clone paths from conf
from multiproject.core.configuration import conf

# create ssh key store instance
from multiproject.core import ssh_keys
store = ssh_keys.CQDESshKeyStore()

# Check if any update flags exists
if not len(store.get_ssh_key_update_flags()):
    print 'No update flags found so doing nothing.'
    exit()

# TODO read the values from conf
repo_path = conf.gitosis_repo_path
clone_path = conf.gitosis_clone_path
commit_msg = 'SSH keys updated by the script.'

# check that we have a repo
if not os.path.exists(repo_path):
    print 'The repository path does not exist.'
    exit()

# Check if the clone exists
if os.path.exists(clone_path):
    # Perform a git pull
    check_call('git pull', shell=True, cwd=clone_path)
    # TODO try again with a new clone if pull failes
else:
    # Clone the repository
    check_call('git clone %s %s' % (repo_path, clone_path), shell=True)

# empty the keydir
for keyfile in os.listdir(clone_path + '/keydir'):
    os.remove(clone_path + '/keydir/' + keyfile)

# generate the new keys
ok = store.perform_ssh_key_update(clone_path) 
if not ok:
    print "perform_ssh_key_update failed."
    exit()

# add + commit + push
try:
    check_call('git add keydir/\*', shell=True, cwd=clone_path)
    check_call('git commit -a -m "%s"' % commit_msg, shell=True, cwd=clone_path)
    check_call('git push', shell=True, cwd=clone_path)
except:
    print "Warning: git add, commit or push returned non-0 exit status."
    exit()
