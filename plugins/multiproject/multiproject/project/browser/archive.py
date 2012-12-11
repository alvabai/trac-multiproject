# -*- coding: utf-8 -*-
"""
This module implements the archive (zip/tar.gz) export for Mercurial, Git and SVN repositories. SVN

Module contains both request handler and preprocessor for placing the link into alternative navigation.

Example URLs
------------

Git:
    Git supports both names and hashes

    - http://www.service.com/myproject/export/archive
    - http://www.service.com/myproject/export/archive?rev=master
    - http://www.service.com/myproject/export/archive?rev=master&format=zip

Mercurial:
    Mercurial supports both names and hashes

    - http://www.service.com/myproject/export/archive?rev=default&format=tgz
    - http://www.service.com/myproject/export/archive?rev=aec42deab6346234eacaf943996&format=tgz

Subversion:
    Implementation uses Trac's internal changeset functionality, thus only zip is supported.
    The revision is the path in svn, like: trunk, branches/featurex, tags/release-1.0

    - http://www.service.com/myproject/export/archive?rev=trunk&format=zip
    - http://www.service.com/myproject/export/archive?rev=tags/release-1.0&format=zip
    - http://www.service.com/myproject/export/archive?rev=branches/featurex&format=zip


.. NOTE::

    Initially, it was tried to be implemented using Trac's changeset zip renderer, but getting
    the correct files based on changeset range caused some issues

"""
import tempfile
import re
import os
from subprocess import Popen, PIPE

from trac.core import Component, implements, TracError
from trac.util import content_disposition
from trac.versioncontrol import NoSuchChangeset
from trac.versioncontrol.api import RepositoryManager
from trac.web.api import HTTPNotFound, IRequestFilter, IRequestHandler, RequestDone
from trac.web.chrome import add_link
from trac.web.href import Href
from trac.util.translation import _
from trac.util.html import plaintext

from multiproject.common.projects import Project
from multiproject.core.configuration import conf


class ArchiveSourceModule(Component):
    """
    Module uses IRequestFilter interface to add export/archive links into
    browser -page. The actual export archive is implemented in :py:func:`ArchiveSourceModule.process_request`
    """
    implements(IRequestFilter, IRequestHandler)

    # Class variables
    browser_regx = re.compile('^(\/browser)\/?$')
    archive_regx = re.compile('^(\/export)\/archive?$')
    formats = {
        'zip':{'ext':'zip', 'mime':'application/zip', 'desc':'Zip archive'},
        'tgz':{'ext':'tgz', 'mime':'application/x-gzip', 'desc':'Gzip archive'},
    }

    # IRequestFilter methods

    def pre_process_request(self, req, handler):
        """
        Pre-process the request by adding 'Zip Archive' link into alternative format links
        The link is constructed from first and latest revision number, taken from the default
        repository.

        :param Request req: Trac request
        :param object handler: existing handler
        :returns: Handler, modified or not
        """
        # Add link only in /browser or /browser/?rev= pages
        if self.browser_regx.match(req.path_info) and 'BROWSER_VIEW' in req.perm:
            # Get default repository and its type
            rm = RepositoryManager(self.env)
            repo = rm.get_repository('')
            repo_type = rm.repository_type

            # Construct the export urls for each format and based on revision info
            latest_rev = plaintext(str(req.args.get('rev', repo.get_youngest_rev())))

            # Use Trac's internal implementation
            if repo_type == 'svn':
                return handler

            # For other types, iterate supported formats
            for format, info in self.formats.items():
                add_link(req, 'alternate', req.href('export/archive', rev=latest_rev, format=format), _(info['desc']),
                    info['mime'], info['ext'])

        return handler

    def post_process_request(self, req, template, data, content_type):
        """
        Does post processing actions. In this case, none is required.
        """
        return (template, data, content_type)

    # IRequestHandler methods

    def match_request(self, req):
        """
        Checks if this handlers should take care of request or not

        :returns: True if this handler wants to handle the request
        """
        return bool(self.archive_regx.match(req.path_info))


    def process_request(self, req):
        """
        Handle the export requests

        :raises: TracError in case of failure
        """
        req.perm.require('BROWSER_VIEW')

        # Get default repository and its type
        rm = RepositoryManager(self.env)
        repo = rm.get_repository('')
        repo_type = rm.repository_type
        svn_path = 'trunk'
        format = plaintext(req.args.get('format', 'zip'))

        # Get revision info. For svn it's in format: <revnum>/<path>
        revision = plaintext(str(req.args.get('rev', repo.get_youngest_rev())))
        if repo_type == 'svn':
            revision = repo.get_youngest_rev()
            svn_path = req.args.get('rev', svn_path)

        # Validate if given revision really exists
        try:
            revision = repo.normalize_rev(revision)
        except NoSuchChangeset:
            raise HTTPNotFound('No such changeset')

        # Validate format
        if format not in self.formats:
            raise TracError('Format is not supported')

        # Load project object based on current environment
        env_name = conf.resolveProjectName(self.env)
        repo_type = self.env.config.get('trac', 'repository_type')
        repo_dir = conf.getEnvironmentVcsPath(env_name)
        project = Project.get(env_name=env_name)

        if repo_type not in conf.supported_scm_systems:
            raise TracError('Non-supported VCS type')

        # Create temporary directory with appropriate subdirectory where to export repository
        tempfd = tempfile.NamedTemporaryFile(delete=False)

        # Dump the repository per type, into defined location
        try:
            if repo_type == 'git':
                # Use short revision format
                revision = revision[:6]
                prefix = '%s-%s' % (env_name, revision[:6])
                self._archive_git(repo_dir, revision, format, tempfd.name, prefix)

            elif repo_type == 'hg':
                # In case of both local:global revision format, use only global
                if ':' in revision:
                    revision = revision.split(':', 1)[1]
                prefix = '%s-%s' % (env_name, revision[:6])
                self._archive_hg(repo_dir, revision, format, tempfd.name, prefix)

            elif repo_type == 'svn':
                assert format == 'zip', 'Only zip format is supported for subversion'

                # Redirect to Trac's internal changeset functionality
                # Example: https://localhost/svnproject/changeset/4/trunk?old_path=%2F&format=zip
                changeset_href = Href('/%s/changeset' % env_name)
                return req.redirect(changeset_href(revision, svn_path, old_path='/', format='zip'))

        # Redirect raises RequestDone: re-raise it
        except RequestDone:
            raise

        except Exception, err:
            self.env.log.exception('Repository dump failed: %s' % err)
            raise TracError('Repository archive failed - please try again later')

        finally:
            # Ensure the temp file gets removed even on errors
            if os.path.exists(tempfd.name):
                os.remove(tempfd.name)

        # Create HTTP response by reading the archive into it
        try:
            req.send_response(200)
            req.send_header('Content-Type', self.formats[format]['mime'])
            inline = '%s-%s.%s' % (project.env_name, revision, self.formats[format]['ext'])
            req.send_header('Content-Disposition', content_disposition('inline', inline))
            content = tempfd.read()
            req.send_header("Content-Length", len(content))
            req.end_headers()
            req.write(content)
            tempfd.close()

        # Ensure the temp file gets removed
        finally:
            if os.path.exists(tempfd.name):
                os.remove(tempfd.name)

        raise RequestDone

    def _archive_git(self, srcdir, revision, format, archpath, prefix=None):
        """
        Create archive from Git repository

        :param str srcdir: Path to Git repository
        :param str revision: Name or hash identifier of the parent revision
        :param str format: Archive format. Git supports zip, tar, tar.gz, tgz
        :param str archpath: Absolute path to archive
        :param str prefix: Prefix to use in archive, uses revision if not given
        :returns: Path to archive
        :raises: Exception in a case of failure
        """
        if format not in ('zip', 'tar', 'tgz', 'tar.gz'):
            raise ValueError('Unsupported archive format %s' % format)
        if prefix is None:
            prefix = revision

        git = self.env.config.get('git', 'git_bin', 'git')
        # NOTE: For consistency, use prefix to create path structure (because Mercurial always wants to set prefix)
        cmd = [git, 'archive', '--prefix', prefix + '/', '--output', archpath, '--format', format, revision]
        self.env.log.info('Dumping git repository: %s (from %s)' % (cmd, srcdir))
        popen = Popen(cmd, cwd=srcdir, stdout=PIPE, stderr=PIPE, close_fds=True)
        stdout, stderr = popen.communicate()

        # Raise exception in case of returncode != 0
        if popen.returncode:
            raise Exception('Process failed: %s %s (%s) ' % (stdout, stderr, popen.returncode))

        return archpath

    def _archive_hg(self, srcdir, revision, format, archpath, prefix=None):
        """
        Create archive from Mercurial repository

        :param str srcdir: Path to hg repository
        :param str revision: Name or hash identifier of the parent revision
        :param str format: Archive format. Hg supports zip, tar, tgz, tbz2, uzip
        :param str archpath: Absolute path to archive
        :param str prefix: Prefix to use in archive, uses revision if not given
        :returns: Path to archive
        :raises: Exception in a case of failure
        """
        if format not in ('zip', 'tar', 'tgz', 'tbz2', 'uzip'):
            raise ValueError('Unsupported archive format %s' % format)
        if prefix is None:
            prefix = revision
        # NOTE: Mercurial always wants to set prefix (files are located in subfolder)
        cmd = ['hg', '-R', srcdir, 'archive', '--type', format, '--prefix', prefix, '--rev', revision, archpath]
        self.env.log.info('Dumping hg repository: %s (from %s)' % (' '.join(cmd), srcdir))
        popen = Popen(cmd, stdout=PIPE, stderr=PIPE, close_fds=True)
        stdout, stderr = popen.communicate()

        # Raise exception in case of returncode != 0
        if popen.returncode:
            raise Exception('Process failed: %s %s (%s) ' % (stdout, stderr, popen.returncode))

        return archpath
