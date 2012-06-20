# -*- coding: utf-8 -*-
"""
Contents of the module:

- Command: Run command with/without sudo, authenticated against the defined auth backed
- FileManager: Upload/download files while authenticating with defined auth backed
- DatabaseManager: Helper class to read connection information from the setup and providing database related actions
- Service: Subclass of Command running service actions against /etc/init.d/<service>
- Apache: Subclass of Service to automatically handle httpd/apache2 name differences
- Config: fabfile.ini configuration reader
- RemoteConfigReader: Reads ini file from remote host

"""
__author__ = 'jumuston'

import ConfigParser
import sys
import os
from datetime import datetime

from fabric import api
from fabric.state import env
from fabric.contrib import files

from fablib.base import config, logger
from fablib.auth import Auth


class Command(object):
    """
    Base class for commands, with few changes on top of normal Fabric functionality:

    - sudo: Try to read sudo password from user's home directory, txt file.
    - run: Optional parameters are given on top of Command initialization

    >>> cmd = Command('uptime')
    >>> cmd.sudo()              # Run as root and without parameters
    >>> cmd.run('-V')           # Run as normal user and with given parameter

    """
    def __init__(self, cmd):
        self.cmd = cmd


    def run(self, use_sudo=True, *args):
        """
        Runs the command with optional arguments.
        If use_sudo flag is set to True, command runs with sudo rights.
        """
        if use_sudo:
            return self.sudo(*args)
        return api.run('%s %s' % (self.cmd, ' '.join(args)))


    def sudo(self, *args):
        """
        Runs sudo command by first reading the password
        from home directory (convention in production environments)

        .. NOTE::

            Following methods are equalent:

            >>> cmd = Command('uptime')
            >>> cmd.run(use_sudo=True)
             12:02:49 up  3:57,  2 users,  load average: 0.64, 0.62, 0.63
            >>> cmd.sudo()
             12:02:50 up  3:57,  2 users,  load average: 0.64, 0.62, 0.63

        """
        Auth().authenticate(env)

        cmd = '%s %s' % (self.cmd, ' '.join(args))
        output = api.sudo(cmd)

        return output


class FileManager(object):
    """
    File management class, adding some extra functionality on top of fabric solution.
    """
    def put(self, local_path, remote_path, use_sudo=False):
        """
        Upload file to remote location.
        """
        Auth().authenticate(env)
        return api.put(local_path=local_path, remote_path=remote_path, use_sudo=use_sudo)


    def get(self, remote_path, local_path):
        """
        Download file from remote location.
        """
        Auth().authenticate(env)
        return api.get(remote_path=remote_path, local_path=local_path)


    def exists(self, remote_path, use_sudo=False):
        """
        Return True if file exists on remote host, otherwise False

        This implementation is based on fabric.files: This function
        adds support for environment variables and expanding tilde
        """

        # NOTE: In case bash shows some output when opened, the files.exists
        # gets broken: In such case, show warning and take last line
        if len(remote_path.splitlines()) > 1:
            logger.warn('Remote path is actually multiliner - taking the last row')
            remote_path = str(remote_path.splitlines()[-1]).strip()

        if '~' in remote_path:
            with api.settings(api.hide('stdout', 'running')):
                homepath = run('echo $HOME', use_sudo=use_sudo)
                remote_path = remote_path.replace('~', homepath)

        found = files.exists(remote_path, use_sudo=use_sudo)
        logger.debug('Checked if exists: %s = %s' % (remote_path, found))

        return found


class DatabaseManager(object):
    """
    Class for doing DB related actions via Fabric
    """
    def __init__(self, database_name='trac_admin'):
        conf_dir = config['trac_conf_path']
        rcr = RemoteConfigReader(os.path.join(conf_dir, 'project.ini'))
        confdict = dict(rcr.items('multiproject'))

        self.params = {
            'user': confdict['db_user'],
            'password': confdict['db_password'].strip(),
            'name': database_name,
            'host': confdict['db_host']
        }


    def dump(self):
        """
        Dumps the specified database and returns location of dump back

        Uses configurable 'tmp_dir' on remote host to temporarily
        """
        cmd = 'mysqldump -u %(user)s -h %(host)s -p%(password)s %(name)s > %(file)s'
        if not self.params['password']:
            cmd = cmd.replace('-p%(password)s', '')

        date = datetime.utcnow().strftime('%Y%m%d-%H%M')
        dumpname = '%s-%s.dump.sql' % (self.params['name'], date)
        dumpdir = config['tmp_dir']
        dumppath = os.path.join(dumpdir, dumpname)

        # Add dump specific parameters
        self.params.update({'dumppath':dumppath, 'file':dumppath})

        logger.info('Dumping database %s to %s' % (self.params['name'], dumppath))
        run(cmd % self.params)

        return dumppath


    def run(self, sql, regexp=None):
        """
        Runs given SQL to remote database

        - sql: SQL to run. Remember to end with semicolon or \G
        - regexp: Optional compiled regexp to match with results. Example of regexp object: re.compile(r'(\d+)', re.MULTILINE)

        """
        cmd = 'mysql -u %(user)s -h %(host)s -p%(password)s -e "%(sql)s" %(name)s '
        if not self.params['password']:
            cmd = cmd.replace('-p%(password)s', '')

        # Strip linefeeds
        sql = ' '.join([line.strip() for line in sql.replace('"', '\"').splitlines()])
        self.params.update({'sql':sql})
        output = run(cmd % self.params)

        # If regexp is given, match it with output
        if regexp:
            match = regexp.search(output)
            if match:
                return match.group(1)

        return output


class Service(Command):
    """
    Service commands
    """
    def __init__(self, name):
        """
        Initiate service command. Automatically using service if found.
        """
        self.cmd = '/etc/init.d/%s' % name
        if exists('/usr/sbin/service'):
            self.cmd = '/usr/sbin/service %s' % name


    def start(self):
        return self.sudo('start')


    def status(self):
        return self.sudo('status')


    def restart(self):
        return self.sudo('restart')


    def stop(self):
        return self.sudo('stop')


class Apache(Service):
    """
    Apache service - automatically uses httpd/apache2 based on environment
    """
    def __init__(self):
        apache = '/etc/init.d/apache2'
        httpd = '/etc/init.d/httpd'

        if exists(apache):
            super(Apache, self).__init__('apache2')
        elif exists(httpd):
            super(Apache, self).__init__('httpd')
        else:
            raise Exception('Apache service cannot be found')


class RemoteConfigReader(object):
    """
    Configuration reader for remote files.
    In a case of fabfile.ini, use :class:`Config` instead.
    """
    def __init__(self, remote_path):
        self.remote_path = remote_path

        if not exists(remote_path):
            raise Exception('Configuration file %s cannot be found' % remote_path)

        # Retrieve remote path to local for reading
        self.local_path = os.path.join(config['tmp_dir'], 'remoteconf.ini')
        if os.path.exists(self.local_path):
            os.unlink(self.local_path)
        get(remote_path, self.local_path)

    def items(self, section):
        scp = ConfigParser.SafeConfigParser()
        scp.readfp(open(self.local_path))

        return scp.items(section)

    def get(self, key, section):
        confdict = dict(self.items(section))
        return confdict[key].strip()


def run(command, use_sudo=False):
    """
    Run run command using Command class - to resemble Fabric run.
    """
    cmd = Command(command)
    return cmd.run(use_sudo=use_sudo)


def sudo(command):
    """
    Run sudo command using Command class - to resemble Fabric sudo.
    """
    return run(command, use_sudo=True)


def abort(msg):
    """
    Print error message and abort execution
    """
    print msg
    return sys.exit(-1)


# Export file actions
put = FileManager().put
get = FileManager().get
exists = FileManager().exists
