===============
Troubleshooting
===============
Having problems with the setup? This chapter gives few pointers what to expect and where look into.
As a thumb of rule, in a case of problems, :ref:`see multiproject log first <trouble-log>`

.. contents::
   :local:

.. _trouble-log:

Logging
=======
By default, project specific log files are disabled but they all write in centralized location instead::

    /var/log/trac/multiproject.log

The logging configuration, includeing the logging level is can be changed in ``project.ini``:

.. code-block:: ini

    [logging]
    log_file = /var/www/trac/logs/multiproject.log
    log_level = ERROR
    log_type = factory:multiproject.core.log,logger_factory
    log_format = $(asctime)s Trac[$(basename)s:$(module)s] $(levelname)s: $(message)s

.. note:: Patch required

    Centralized logging requires patch ``logging.patch`` to be applied to Trac.

Procedure failed
================
Getting following kind of error logs?::

    Exception. get_all_user_groups(37) procedure failed.

The problem is likely because of database user rights. See :ref:`install-server-db`


LDAP: Database already in use
=============================
Following error is given when accessing the LDAP from command, for example with ``slapadd``::

      hdb_db_open: database "dc=it,dc=local": database already in use.
      backend_startup_one (type=hdb, suffix="dc=it,dc=local"): bi_db_open failed! (-1)
      slap_startup failed

Stop the service and run the command again.

Apache: Could not open configuration
====================================
If Apache fails to start because of error:

    Starting httpd: httpd: Syntax error on line 222 of /etc/httpd/conf/httpd.conf:
    Could not open configuration file /var/www/trac/config/multiproject.conf: Permission denied

it may be because of the insufficient file permissions or SELinux is limiting down the access.
To fix both::

    sudo chown -R apache.apache /var/www/trac/config
    sudo chcon -t httpd_config_t /var/www/trac/config/multiproject.conf
    sudo chcon -t httpd_config_t /var/www/trac/config/multiproject-access.conf


Reference: http://forums.fedoraforum.org/archive/index.php/t-106655.html

.. _trouble-env-init:

Trac environment initialization
===============================
Usually projects are created via web UI. However, when creating a new setup or environment from command
line, following errors can appear with command::

    sudo trac-admin /var/www/trac/projects/home initenv home \
    mysql://tracuser:********@localhost/home --inherit=/var/www/trac/config/project.ini

Error: OperationalError: (1050, "Table 'system' already exists"):
    Database already exists and it already contains the Trac tables. Drop the tables or
    drop whole the database and recreate it::

        mysql -u tracuser -p
        mysql> drop database home;
        mysql> create database home default character set utf8;

Initenv for '/var/www/trac/projects/home' failed. Does an environment already exist?
    Environment already exists in filesystem. Remove the folder and run the command again.

Environment not found
=====================
This error message may come from various reasons:

- See :ref:`trouble-log`
- See :ref:`trouble-env-init`
- See :ref:`trouble-import`

.. _trouble-import:

Import errors
=============
Multiproject module structure is somewhat monolithic, requiring all the dependencies to be installed.
If the service is not starting properly, try following from python shell (start with command: ``python``):

.. code-block:: pycon

    >>> from multiproject import core
    >>> from multiproject import home
    >>> from multiproject import project
    from multiproject import common
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/usr/lib/python2.6/site-packages/TracMultiProject-1.1.15-py2.6.egg/multiproject/common/__init__.py", line 4, in <module>
        from multiproject.common import users
      File "/usr/lib/python2.6/site-packages/TracMultiProject-1.1.15-py2.6.egg/multiproject/common/users/__init__.py", line 2, in <module>
        from login import *
      File "/usr/lib/python2.6/site-packages/TracMultiProject-1.1.15-py2.6.egg/multiproject/common/users/login.py", line 16, in <module>
        from multiproject.core.auth.auth import Authentication
      File "/usr/lib/python2.6/site-packages/TracMultiProject-1.1.15-py2.6.egg/multiproject/core/auth/__init__.py", line 1, in <module>
        import mod_python_access
      File "/usr/lib/python2.6/site-packages/TracMultiProject-1.1.15-py2.6.egg/multiproject/core/auth/mod_python_access/__init__.py", line 6, in <module>
        from hg import *
      File "/usr/lib/python2.6/site-packages/TracMultiProject-1.1.15-py2.6.egg/multiproject/core/auth/mod_python_access/hg.py", line 1, in <module>
        from multiproject.core.auth.hg_access import MercurialAccessControl
      File "/usr/lib/python2.6/site-packages/TracMultiProject-1.1.15-py2.6.egg/multiproject/core/auth/hg_access.py", line 1, in <module>
        from mercurial.hgweb.hgweb_mod import perms
    ImportError: No module named mercurial.hgweb.hgweb_mod

In this case, the mercurial module is missing. Install the module and try again.


ImportError: cannot import name wireproto
=========================================
If the mercurial version is too old, following may be given::

    from mercurial import wireproto
    ImportError: cannot import name wireproto

Try installing newer version::

    sudo pip install --upgrade mercurial


Cannot find an implementation of the "WelcomeModule"
====================================================
Trac cannot find some of the registered components. This may be due non-egg installation:
While .egg packaging format is less preferred, it is still widely used/required by Trac plugins.
To ensure the plugin gets correctly loaded, install it as an egg (use ``-Z`` to extract the package)::

    cd SomeCustomPlugin/
    python setup.py bdist_egg
    easy_install -Z dist/*.egg

Also, ensure the egg contains all the required egg info files::

    unzip -l SomeCustomPlugin-py2.6.egg |grep EGG-INFO

         7847  2012-04-10 13:30   EGG-INFO/SOURCES.txt
            1  2012-04-10 13:30   EGG-INFO/dependency_links.txt
          212  2012-04-10 13:30   EGG-INFO/entry_points.txt
            1  2012-04-10 13:30   EGG-INFO/not-zip-safe
           13  2012-04-10 13:30   EGG-INFO/top_level.txt
          202  2012-04-10 13:30   EGG-INFO/PKG-INFO

.. seealso:: :ref:`trouble-import`

Failed to create SVN repository
===============================
Creating version control repositories requires a capability to run shell commands.
In a case of SVN, the user running the Apache requires also the :envvar:`HOME` environment variable as
it defaults to ``root`` account::

    svnadmin: Can't open file '/root/.subversion/servers': Permission denied

To fix the issue, set :envvar:`HOME` variable in Apache startup script ``/etc/init.d/apache2``::

    export HOME=/var/www/trac


SSL handshake failed
====================
When getting following SSL related errors::

    SSL handshake failed: SSL error: A TLS warning alert has been received.
      or
    httpd: Could not reliably determine the server's fully qualified domain name, using 127.0.0.1 for ServerName

To fix the issue, add a ``ServerName`` directive *outside of any virtual host*, having same value as the
:ref:`SSL certificate contains <install-apache>`::

    ServerName myhost

