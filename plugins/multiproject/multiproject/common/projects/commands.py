# -*- coding: utf-8 -*-

"""
This package contains classes used when creating and removing projects

Commander stacks and runs Commands and can roll them back (at least should ;)
Command is an abstract base class used by all commands
All heir of Command together forms a project creation process
"""

import os, shutil
from subprocess import Popen, PIPE
from datetime import datetime
from ConfigParser import ConfigParser

from trac.admin import console
from trac.config import Configuration
from trac.util.datefmt import to_utimestamp, utc

from multiproject.core.cache.project_cache import ProjectCache
from multiproject.core.files.files_conf import FilesConfiguration, FilesDownloadConfig
from multiproject.core.permissions import CQDEUserGroupStore
from multiproject.core.configuration import conf
from multiproject.core.util import filesystem
from multiproject.core.db import admin_transaction, admin_query, db_transaction, safe_string, safe_int


class Command(object):
    """ Abstract base class defining skeleton of any command
    """
    def __init__(self):
        self.success = False
        self.name = "Command"
        self.errormsg = ""

    def do(self):
        # Failed: execution should not come here
        return None

    def undo(self):
        # Failed: execution should not come here
        return None


class CreateTracDatabase(Command):
    """ Creates database schema for a project to be created. Project needs it's
        own database schema for keeping track of project specific stuff.
    """
    def __init__(self, project):
        Command.__init__(self)
        self.dbname = safe_string(project.env_name)
        self.name = "CreateTracDatabase"

    def do(self):
        # Create db (schema)
        with admin_transaction() as cursor:
            # Create database
            try:
                query = """
                CREATE DATABASE `{0}`
                DEFAULT CHARACTER SET utf8 COLLATE utf8_bin
                """.format(safe_string(self.dbname))
                cursor.execute(query)
            except:
                conf.log.exception("Error occurred on creating database! %s" % query)
                return False

        self.success = True
        return True

    def undo(self):
        # Remove only if command was executed successfully
        if self.success:
            with admin_transaction() as cursor:
                try:
                    # Remove database
                    cursor.execute("DROP DATABASE `{0}`".format(safe_string(self.dbname)))
                except Exception:
                    conf.log.exception('Failed to drop database: {0}'.format(self.dbname))
                    return False
        return True


class CloneVersionControl(Command):
    """ Command for cloning existing repository for a project
    """
    def __init__(self, project):
        Command.__init__(self)
        self.project = project
        self.name = "CloneVersionControl"

    def do(self):
        parent = self.project.parent_project

        if not parent:
            conf.log.error("Cloning failed! Parent not found!")
            return False
        try:
            parent_path = conf.getEnvironmentVcsPath(parent.env_name)
        except Exception:
            conf.log.exception("Parent repository path could not be resolved! %s" % parent.env_name)
            return False

        try:
            project_path = conf.getEnvironmentVcsPath(self.project.env_name)
        except Exception:
            conf.log.exception("Project repository path could not be resolved. %s" % parent.env_name)
            return False

        try:
            shutil.copytree(parent_path, project_path)
        except OSError as err:
            conf.log.error("Could not clone existing version control system. %s => %s (%s)" %
                           (parent_path, project_path, err.strerror))
            return False

        self.success = True
        return True

    def undo(self):
        if self.success:
            try:
                filesystem.rmtree(self.vcs_path)
            except:
                conf.log.exception('Failed to delete repository: {0}'.format(self.vcs_path))
                return False
        return True


class CreateTracVersionControl(Command):
    """ Command for creating repository for a trac project to be created
    """
    def __init__(self, project, settings):
        Command.__init__(self)
        self.vcs_path = conf.getEnvironmentVcsPath(project.env_name)
        self.vcs_type = settings['vcs_type']
        self.name = "CreateTracVersionControl"

    def do(self):
        self.success = False

        # Create target directory if missing
        if not os.path.exists(self.vcs_path):
            os.makedirs(self.vcs_path)

        # Subversion repository
        if self.vcs_type == 'svn':
            self.success = self._run(('svnadmin', 'create', self.vcs_path))

        # Mercurial repository
        elif self.vcs_type == 'hg':
            if self._run(('hg', 'init', self.vcs_path)):
                with open(os.path.join(self.vcs_path, '.hg/hgrc'), 'w+b') as hgrc:
                    hgrc.write("[web]\npush_ssl = false\n\n")
                self.success = True

        # GIT repository
        elif self.vcs_type == 'git':
            if self._run(('git', '--bare', '--git-dir', self.vcs_path, 'init', '--shared=true')):
                self._run(('git', '--git-dir', self.vcs_path, 'update-server-info'))
                self.success = True

        # Unknown repository type
        else:
            conf.log.debug("Unsupported version control type %s" % self.vcs_type)

        return self.success

    def undo(self):
        if self.success:
            try:
                filesystem.rmtree(self.vcs_path)
            except Exception, e:
                conf.log.exception('Failed to remove version control directory: {0}'.format(self.vcs_path))
                return False
        return True

    def _run(self, args):
        """
        Runs the command sequence using ``subprocess.Popen``
        while logging the possible problems.

        :param tuple args: Command parts. Example ``('svnadmin', 'create', pathvar)``
        :returns: True on success, otherwise False
        """
        try:
            # Run system command
            proc = Popen(args, stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()

            if proc.returncode:
                conf.log.error("Failed to run repository command %s for %s in %s: %s" %
                               (' '.join(args), self.vcs_type, self.vcs_path, stderr))
                return False

        except Exception:
            conf.log.exception('Failed to run command: %s' % ' '.join(args))
            return False

        return True


class InitCommitHooks(Command):
    def __init__(self, project, settings):
        Command.__init__(self)
        self.vcs_path = conf.getEnvironmentVcsPath(project.env_name)
        self.vcs_type = settings['vcs_type']
        self.name = "InitCommitHooks"
        self.hooks = {'git': self._git_hook,
                      'hg': self._hg_hook,
                      'svn': self._svn_hook}

    def do(self):
        try:
            return self.hooks[self.vcs_type]()
        except Exception:
            return False

    def undo(self):
        """ This change can not be undone
        """
        return True

    def _git_hook(self):
        hook = os.path.join(conf.version_control_hooks_dir, "git-incoming")
        link_name = os.path.join(self.vcs_path, "hooks/post-receive")
        return self.symlink(hook, link_name)

    def _svn_hook(self):
        hook = os.path.join(conf.version_control_hooks_dir, "svn-incoming")
        link_name = os.path.join(self.vcs_path, "hooks/post-commit")
        return self.symlink(hook, link_name)

    def _hg_hook(self):
        # In hg, hooks can be set in config
        hgrc = "%s/.hg/hgrc" % self.vcs_path
        parser = ConfigParser()
        files = parser.read(hgrc)

        if not files:
            conf.log.warning("Failed to find mercurial config: {0}".format(hgrc))
            return False

        try:
            # Set hook
            path = os.path.join(conf.version_control_hooks_dir, "hg-incoming")
            if 'hooks' not in parser.sections():
                parser.add_section('hooks')
            parser.set('hooks', 'incoming', path)

            # Write hook in config
            with open(hgrc, "w") as hgrc_file:
                parser.write(hgrc_file)

        except Exception:
            conf.log.exception("Failed to hook with mercurial repository")
            return False

        return True

    def symlink(self, source, dst):
        """
        Creates a symlink between ``source`` and ``dst``
        If the destination already exists, it will be deleted first.

        Returns True on success and False on error
        """
        try:
            # Delete old post-commit file if already exists
            if os.path.exists(dst):
                os.unlink(dst)
            # Link to new file
            os.symlink(source, dst)
        except Exception:
            conf.log.exception("Failed hooking {0} repository".format(self.vcs_path))
            return False

        return True


class CreateTracEnvironment(Command):
    """ This creates actual trac environment/project
    """
    def __init__(self, project, settings):
        Command.__init__(self)
        self.vcs_type = settings['vcs_type']
        self.short_name = project.env_name
        self.long_name = project.project_name
        self.author = project.author
        self.env_path = conf.getEnvironmentSysPath(self.short_name)
        self.db_string = conf.getEnvironmentDbPath(self.short_name)
        self.vcs_path = conf.getEnvironmentVcsPath(self.short_name)
        self.args = "'" + self.long_name + "'" + " " + self.db_string
        self.args += " " + self.vcs_type + " " + self.vcs_path
        self.args += " --inherit=" + conf.global_conf_path
        self.name = "CreateTracEnvironment"

    def do(self):
        # Create environment
        try:
            tracadmin = console.TracAdmin(self.env_path)
            error = tracadmin.do_initenv(self.args)
            if error == 2:
                conf.log.error("Could not create trac environment on %s with args: %s" %
                               (self.env_path, str(self.args)))
                return False
        except Exception:
            conf.log.exception("Could not create trac environment on {0} with args: {1}".format(
                self.env_path,
                self.args)
            )
            return False

        self.success = True
        return True

    def undo(self):
        try:
            filesystem.rmtree(self.env_path)
        except Exception:
            conf.log.exception('Failed to delete trac environment: {0}'.format(self.env_path))
            return False
        return True


class ConfigureTrac(Command):
    """ When project is created, plugins needs to be properly configured
    """
    def __init__(self, project, settings):
        Command.__init__(self)
        self.project = project
        self.env_path = conf.getEnvironmentSysPath(project.env_name)
        self.conf_file = self.env_path + '/conf/trac.ini'
        self.conf_file_back = self.conf_file + '.back'
        self.vcs_type = settings['vcs_type']
        self.name = "ConfigureTrac"

    def do(self):
        # Make backup of trac.ini before configuring it
        try:
            shutil.copy(self.conf_file, self.conf_file_back)
        except Exception:
            conf.log.exception("Could not create trac.ini backup")
            return False

        # Open trac.ini for configuration
        config = None
        try:
            config = Configuration(self.conf_file)
        except Exception:
            conf.log.exception("Error while reading config file!")
            return False

        # Enable correct plugin for repository
        try:
            vcs_plugin = self.__vcs_plugin()
            if vcs_plugin:
                config.set('components', vcs_plugin, 'enabled')

            config.set('trac', 'repository_type', self.vcs_type)
        except Exception:
            conf.log.exception("Could not set static settings for trac")
            return False

        try:
            config.set('project', 'descr', self.project.description)
        except Exception:
            conf.log.exception("Couldn't set description")
            return False

        # Remove attachment size (to enable global setting)
        try:
            config.remove("attachment", "max_size")
        except Exception:
            conf.log.exception("Could not remove attachment config property for a new project")

        # Save configuration
        try:
            config.save()
        except Exception:
            conf.log.exception("Failed to save configuration")
            return False

        self.success = True
        return True

    def undo(self):
        if self.success:
            try:
                shutil.move(self.conf_file_back, self.conf_file)
            except:
                conf.log.exception('Failed to move configuration file')
                return False
        return True

    def __vcs_plugin(self):
        """ Returns plugin name that should be enabled
            If no plugin is needed to be enable, returns None
        """
        vcs_plugin_names = {'git': 'tracext.git.*',
                            'hg': 'tracext.hg.*',
                            'cvs': 'tracext.cvs.*',
                            'perforce': 'p4trac.api.*',
                            'bzr': 'tracbzr.*',
                            'clearcase': 'tracext.clearcase.*'}

        if self.vcs_type in vcs_plugin_names:
            return vcs_plugin_names[self.vcs_type]
        else:
            return None


class ListUpProject(Command):
    """ Inserts project data into database that holds global project information
    """
    def __init__(self, project):
        Command.__init__(self)
        self.short_name = project.env_name
        self.long_name = project.project_name
        self.author = project.author
        self.description = project.description
        self.name = "ListUpProject"

        self.project = project
        # Parent is null or project id
        self.parent = None
        if project.parent_id:
            self.parent = safe_int(project.parent_id)

    def do(self):
        params = (self.long_name.encode('utf-8'),
                  self.short_name,
                  self.description,
                  self.author.id,
                  self.parent)

        with admin_query() as cursor:
            try:
                cursor.callproc('create_project', params)
            except:
                conf.log.exception("Listing up project failed.")
                return False

        self.project.refresh()
        self.success = True
        return True

    def undo(self):
        if not self.success:
            return True

        query_get = """
        SELECT trac_environment_key
        FROM projects
        WHERE environment_name = %s
        """
        query_str = """
        DELETE FROM trac_environment
        WHERE identifier = %s
        """
        cache = ProjectCache.instance()

        with admin_transaction() as cursor:
            try:
                cursor.execute(query_get, self.short_name)
                row = cursor.fetchone()
                cursor.execute(query_str, self.short_name)
                if row:
                    cache.clearProject(row[0])

                cache.clearProjectId(self.short_name)
            except Exception:
                conf.log.exception('Failed to removed project {0} from database'.format(self.short_name))
                return False

        return True


class SetPermissions(Command):
    """ When project is created, users should have some initial permissions.
        For example user who created project should be TRAC_ADMIN.

        permissions of constructor holds dictionary of subject => action pairs
        used for giving initial permissions for project
    """
    def __init__(self, project):
        Command.__init__(self)
        self.project = project
        self.name = "SetPermissions"

    def do(self):
        store = CQDEUserGroupStore(self.project.trac_environment_key)
        author = self.project.author

        # Set default groups (adds also author to Owner)
        try:
            firstDone = False
            for grpname, rightslist in conf.default_groups:
                store.create_group(grpname)

                # add the user only to the first group
                # NOTE: Creates the group defined by grpname
                if not firstDone:
                    # Do not validate group permissions on creation
                    store.add_user_to_group(author.username, grpname, validate=False)
                    firstDone = True

                for right in rightslist:
                    store.grant_permission_to_group(grpname, right)
        except:
            conf.log.exception("Could not setup initial permissions")
            return False

        try:
            if conf.private_auth_group:
                auth_group_name, auth_priv = conf.private_auth_group
                # Do not validate group permissions on creation
                store.add_user_to_group('authenticated', auth_group_name)
                for priv in auth_priv:
                    store.grant_permission_to_group(auth_group_name, priv)
        except Exception:
            conf.log.exception("Could not setup initial permissions")
            return False
        return True

    def undo(self):
        # Can't undo this.
        return True


class MakeProjectPublic(Command):
    """ Makes project public
    """
    def __init__(self, project):
        Command.__init__(self)
        self.project = project
        self.name = "MakeProjectPublic"

    def do(self):
        store = CQDEUserGroupStore(self.project.trac_environment_key)

        try:
            # Create anon group and give permissions
            anon_group_name, anon_priv = conf.public_anon_group
            store.add_user_to_group('anonymous', anon_group_name)
            for priv in anon_priv:
                store.grant_permission_to_group(anon_group_name, priv)

            # Create auth group and give permissions
            auth_group_name, auth_priv = conf.public_auth_group
            store.add_user_to_group('authenticated', auth_group_name)
            for priv in auth_priv:
                store.grant_permission_to_group(auth_group_name, priv)

            # Clear project cache
            pc = ProjectCache.instance()
            pc.clearProject(self.project.id)

        except Exception:
            conf.log.exception("Could not make project public")
            return False
        return True

    def undo(self):
        store = CQDEUserGroupStore(self.project.trac_environment_key)

        try:
            anon_group_name, anon_priv = conf.public_anon_group
            auth_group_name, auth_priv = conf.public_auth_group

            store.remove_group(anon_group_name)
            store.remove_group(auth_group_name)

            # Clear project cache
            pc = ProjectCache.instance()
            pc.clearProject(self.project.id)

        except Exception, e:
            conf.log.exception("Could not make project private")

        return True


class CreateDav(Command):
    def __init__(self, project):
        Command.__init__(self)
        self.name = "CreateDav"
        self.dav_sys_path = project.dav_fs_path
        conf.log.debug(self.dav_sys_path)

    def do(self):
        if not os.path.exists(self.dav_sys_path):
            os.makedirs(self.dav_sys_path)
            if not os.path.exists(self.dav_sys_path):
                conf.log.error("Cannot create WebDAV.")
                return False
        return True

    def undo(self):
        if os.path.exists(self.dav_sys_path):
            try:
                filesystem.rmtree(self.dav_sys_path)
            except Exception:
                conf.log.exception('Failed to remove WebDAV folder')
                return False
        return True

class CreateFilesDownloads(Command):
    def __init__(self, project):

        # Import this here to avoid circular references

        Command.__init__(self)
        self.name = "CreateFilesDownloads"
        self.project = project
        self.default_directory = FilesConfiguration().default_downloads_directory
        self.download_config = FilesDownloadConfig(self.project.env_name)
        self.downloads_dir = filesystem.safe_path(self.download_config.base_path.encode('utf-8'),
            self.default_directory)

    def do(self):
        conf.log.warning('CreateFilesDownloads self.files_downloads_sys_path %s'%self.downloads_dir)
        if not os.path.exists(self.downloads_dir):
            try:
                conf.log.warning('CreateFilesDownloads os.makedir %s'%self.downloads_dir)
                os.makedirs(self.downloads_dir)
            except Exception:
                conf.log.exception('Failed to create project files downloads: "%s"'
                    % self.downloads_dir)
            if not os.path.exists(self.downloads_dir):
                conf.log.error("Cannot create files downloads")
                return False
        try:
            self.download_config.downloads_dir = self.default_directory
            self.download_config.save()
        except Exception:
            conf.log.exception("Exception. CreateFilesDownloads save failed.")
            return False

        return True

    def undo(self):
        try:
            self.download_config.delete()
        except Exception:
            conf.log.exception("Exception. CreateFilesDownloads delete failed.")
            return False
        if os.path.exists(self.downloads_dir):
            try:
                filesystem.rmtree(self.downloads_dir)
            except Exception:
                conf.log.exception('Failed to remove project files downloads')
                return False

        return True

class CreateDownloads(Command):
    def __init__(self, project):
        Command.__init__(self)
        self.name = "CreateDownloads"
        self.downloads_sys_path = conf.makeEnvironmentDownloadsPath(project.env_name)

    def do(self):
        if not os.path.exists(self.downloads_sys_path):
            os.makedirs(self.downloads_sys_path)
            if not os.path.exists(self.downloads_sys_path):
                conf.log.error("Cannot create downloads")
                return False
        return True

    def undo(self):
        if os.path.exists(self.downloads_sys_path):
            try:
                filesystem.rmtree(self.downloads_sys_path)
            except Exception:
                conf.log.exception('Failed to remove project downloads')
                return False
        return True


class InitTracWiki(Command):
    """ When project is created some unnecessary wiki is created.
        Remove unnecessary pages here and add more wiki pages if needed.
    """
    def __init__(self, project):
        Command.__init__(self)
        self.project = project
        self.name = "InitTracWiki"

    def do(self):
        # TODO:
        # If project is home or HelpAndSupport, don't delete help wiki pages.
        # See self.project.env_name, home project identifier configuration.
        allowed_pages = ["TitleIndex", "RecentChanges"]
        allowed_pages = ", ".join("'%s'" % x for x in allowed_pages)

        with db_transaction(self.project.env_name) as cursor:
            try:
                cursor.execute("DELETE FROM wiki WHERE name NOT IN (%s)" % allowed_pages)
            except:
                conf.log.exception("InitTracWiki: Cannot delete pages")
                return False

            wikistart = ""
            downloads = ""
            templatef = ""

            # Read templates
            try:
                # TODO: Read files using template processor
                wikipth = "%s/wiki/%s" % (conf.default_theme_path, conf.theme_name)

                templatef = wikipth + "/wikistart.txt"
                wikistart = file(templatef).read()

                templatef = wikipth + "/downloads.txt"
                downloads = file(templatef).read()
            except:
                conf.log.exception("Cannot read template file (%s)." % templatef)
                return False

            try:
                t =  to_utimestamp(datetime.now(utc))
                query = """
                INSERT INTO wiki(name, version, time, author, ipnr, text)
                VALUES
                    ('WikiStart', 1, %s, 'trac', '127.0.0.1', %s),
                    ('Downloads', 1, %s, 'trac', '127.0.0.1', %s)
                """
                cursor.execute(query, (str(t), wikistart, str(t), downloads))
            except Exception:
                conf.log.exception("Failed to initialize project wiki")
                return False

        return True

    def undo(self):
        # Can't revert this
        return True


class TruncateDefaultInformation(Command):
    """ Remove components, milestones and versions
    """
    def __init__(self, project):
        Command.__init__(self)
        self.project = project
        self.name = "TruncateUnnecessaryInformation"

    def do(self):
        with db_transaction(self.project.env_name) as cursor:
            try:
                cursor.execute("TRUNCATE version")
                cursor.execute("TRUNCATE component")
                cursor.execute("TRUNCATE milestone")
            except Exception, e:
                conf.log.exception("Could not truncate trac default information")
                return False
        return True

    def undo(self):
        # Can't revert this
        return True


class ConfigureFilesystemPermissions(Command):
    """ Make sure the project has correct filesystem permissions
    """
    def __init__(self, project):
        Command.__init__(self)
        self.project = project
        self.name = "ConfigureFSPermissions"

        self.env_path = conf.getEnvironmentSysPath(project.env_name)
        self.conf_file = self.env_path + '/conf/trac.ini'
        self.egid = os.getegid()
        self.euid = os.geteuid()

        import stat
        self._perms = {
                 # u+rw,g+r
                 "conf": stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP,
                 # u+rw,g+rw
                 "log": stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP
                 }

    def do(self):
        # TODO: configurable permissions
        try:
            os.chown(self.conf_file, self.euid, self.egid)
            os.chmod(self.conf_file, self._perms['conf'])

            # TODO: Remove hard-coded hack
            logfile = self.env_path + '/log/trac.log'
            if os.path.isfile(logfile):
                os.chown(logfile, self.euid, self.egid)
                os.chmod(logfile, self._perms['log'])
        except Exception, e:
            conf.log.exception("Unable to set filesystem permissions")
            return False

        return True

    def undo(self):
        # Restoring previous permissions here probably isn't worth the effort.
        return True


class ProjectsInfo(object):

    def disk_free(self, dir):
        data = ""
        try:
            pipe = os.popen('{ df -P ' + dir.rstrip() + '|tail -1|awk \'{ print $1","$2","$3","$4 }\'; } 2>&1', 'r')
            data = pipe.read()
            pipe.close()
            if data[-1:] == '\n': data = data[:-1]
        except Exception, e:
            conf.log.exception("Failed to get disk free information")
        return data.split(",")

    def file_modified(self, filename):
        return os.path.getmtime(filename)


class RefreshStatistics(Command):
    """ Refresh all the statistics related with project
    """
    def __init__(self, project):
        Command.__init__(self)
        self.project = project
        self.name = "RefreshStatistics"

    def do(self):
        from multiproject.home.activity import ActivityCalculator

        # Project activity calculation
        ac = ActivityCalculator()
        ac.update_project_activity(self.project.env_name)

        return True

    def undo(self):
        # Can't/No need to undo this.
        return True


class Commander(object):
    """ All commands defined above can be ran with commander. This way commander
        can rollback if exception occurs.
    """
    def __init__(self):
        # Stack is used to stack up commands that are ran
        self.stack = []

    def run(self, command):
        """ Runs and stacks a given command

            Returns True/False of runned command

            If something fails, sets also error message into command
        """
        self._push(command)
        status = False
        try:
            status = command.do()
        except Exception:
            conf.log.exception("Failed to complete command: {0}".format(command.name))
        return status


    def rollback(self):
        """ Rolls back latest command

            Returns boolean of rollback True/False
            or
            None if stack is empty
        """
        command = self._pop()
        if command:
            return command.undo()
        else:
            return None

    def rollallback(self):
        """ All commands that was ran and are stacked are rolled back when
            calling this method
        """
        status = True
        while status:
            status = self.rollback()
        return status

    def _push(self, command):
        """ Internal method for pushing commands into stack
        """
        self.stack.append(command)
        return None

    def _pop(self):
        """ Internal method for taking command from stack

            Returns command on top or None if no commands on stack
        """
        if len(self.stack) > 0:
            return self.stack.pop()
        else:
            return None
