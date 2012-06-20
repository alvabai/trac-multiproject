# -*- coding: utf-8 -*-
'''
Contents of this module
'''
__author__ = 'jumuston'
import os

from fabric.api import task, roles, prompt

from fablib.api import run, sudo, logger, run, get, config
from fablib.utils import Service, Apache, DatabaseManager


@task
def show_status():
    """
    Show short status info about the host
    """
    # Testing
    envvars = ['ROOT', 'PATH', 'LD_LIBRARY_PATH']
    for evar in envvars:
        value = run('echo $%s' % evar)
        print '%s: %s' % (evar, value)


@task
def restart_apache():
    """
    Restart apache service
    """
    apache = Apache()
    print apache.restart()


@task
def show_apache_status():
    """
    Show apache status
    """
    apache = Apache()
    print apache.status()


@task
def restart_memcache():
    """
    Restart memcahced service
    """
    memcached = Service('memcached')
    memcached.restart()


@task
def get_database(name):
    """
    Dumps and loads the specified database dump

    Parameters:
        name = Name of the database to retrieve
    """
    assert name, 'Please provide database name as param: name=<name>'

    # Dump the database. Dumpdir is the location in remote environment
    dbm = DatabaseManager(name)
    dump_path = dbm.dump()
    # Retrieve dump to current folder, with same name as the remote has it
    get(dump_path, os.path.basename(dump_path))


@task
def create_repository(pname=None, rname=None, rtype=None):
    """
    Creates version control repository

    :param str pname: Name of project where to create repository
    :param str rname: Name of repository you want to create
    :param str rtype: Type of the repository you want to create. Valid types are: git, ...

    Example usage::

        fab system.create_repository:myproject,reponame,git

    """
    assert rtype, 'Please provide repository type. Example: git'
    assert pname, 'Please provide project name. Example: myproject'
    assert rname, 'Please provide repository name. Example: reponame'

    root_dir = config['trac_repositories_path']
    repo_dir = os.path.join(root_dir, '%s.%s' % (pname, rname))
    webserver_user = config['webserver_user']
    webserver_group = config['webserver_group']

    # Dictionary for easy-replace
    variables = {
        'rname':rname,
        'pname':pname,
        'rdir':repo_dir,
        'rtype':rtype,
    }

    if rtype == 'git':
        q = 'Creating a %(rtype)s repo "%(rname)s" in %(rdir)s. Is this right (y/n)?' % variables
        if not str(prompt(q, default='n')).lower() == 'y':
            logger.info('Aborting.')
            return

        logger.info('Creating git repository')
        sudo('git --bare --git-dir=%(rdir)s init --shared=true' % variables)
        sudo('git --git-dir=%(rdir)s update-server-info' % variables)
        sudo('chown -R %s:%s %s' % (webserver_user, webserver_group, repo_dir))

        logger.warn('Manual step required. Add following in projects trac.ini')
        print '[repositories]'
        print '%(rname)s.dir = %(rdir)s' % variables
        print '%(rname)s.type = %(rtype)s' % variables
        print ''

    else:
        raise NotImplementedError('Repository type not implemented')


@task
def whoami():
    """
    Show whoami both with and without sudo
    Testing purpose.
    """
    logger.info('Running whoami with sudo: %s' % sudo('whoami'))
    logger.info('Running whoami with user: %s' % run('whoami'))
