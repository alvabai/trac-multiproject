
.. _usage-update:

========
Updating
========
This chapter describes how to update existing MultiProject setup.

.. contents::
   :local:

.. _usage-update-deploy:

Deploy with deploy.sh
=====================
Multiproject comes with simple deploy script, located in package: `scripts/deploy.sh`:

#.  Upload package to server::

        scp multiproject*.tar.gz remotehost:

#.  Extract package (at remote server)::

        tar -xzf multiproject-*.tar.gz
        cd multiproject/
        sudo  ./scripts/deploy.sh -t

    .. note::

        The ``-t`` option installs also the default theme for multiproject.
        The ``-g`` option updates the htdocs from globally installed plugins, which must be used,
        if the static files of the global plugins are used by Apache.
        See ``deploy.sh -h``  for all options.

#.  Restart Apache and Memcache servers

.. _usage-update-fabric:

Deploy with Fabric
==================
Advanced method for updating exiting setup is using the ready-made Fabric_ script.
See :ref:`develop-fabric` for more details how to setup and use the tool.

To deploy the the ``multiproject.tar.gz`` package, run::

    fab -H serverhost dist.deploy:package="dist/multiproject-*-all.tar.gz",\
    opts="--theme --activate"

.. note::

    Internally, the package is extracted and ``scripts/deploy.sh`` is run. This script installs a date and time based
    directory under ``/var/www/trac/dist`` directory.

Fabric task ``dist.deploy`` supports also more native package formats. Based on extention/structure, task
completes the deployment command as follows

- Python source package (.tar.gz): ``pip install --upgrade <packagename>``
- Python egg (.egg): ``easy_install <packagename>``
- RedHat package (.rpm): ``rpm -Uvh <packagename>``
- Debian package (.deb): ``dpk --install <packagename>``


.. _usage-update-db:

Migrate database
================
Whenever there are database changes required, a database migration script is provided inside the multiproject module:
``multiproject.core.migrations`` as python files. These migrations can be run with command (also found in package)::

    # List available migrations
    sudo ./scripts/update.py

Example output (one new migration available)::

    STATUS      MIGRATION
    ---------------------------------------------------------------
    installed : 20110906120000_authentication_method_datatype
    installed : 20111207083300_wiki_start_time_to_utimestamp
    installed : 20120209130000_user_created
    new       : 20120210150000_project_events


    To install migrations
        python update.py --update=[target_migration_name]

    Other options are:
        --update-to=MIGRATION, -t=MIGRATION
            - Runs all migrations up or down to the given name
        --cherry-pick-update=MIGRATION, -p=MIGRATION
            - Tries to update one, single migration. Dangerous!
        --cherry-pick-downgrade=MIGRATION, -d=MIGRATION
            - Tries to downgrade one, single migration. Dangerous!

To run migration step::

    python update.py --update-new


.. _usage-backup-db:

Backup database
===============
It is a good practice to take backups from databases regularly, and especially before :ref:`migrating database <usage-update-db>`.
Because setup consists from multiple database and routines, the MySQL database backup is taken with command::

    mysqldump --all-databases --routines -u root -p > multiproject-`date +%Y%m%d-%H%M%S`.mysqldump.sql

To restore the database dump, run::

    mysql -u root < multiproject-20120405.mysql.sql


.. _usage-org-update:

Update organization info
========================
MultiProject allows to put users into organizations based on authentication backend and/or
email domain.

#.  Update configuration

    Set ``use_organizations = true`` and set organizations rules in configuration::

        [multiproject-users]
        use_organizations = true
        # org.<auth|email>.<position> = <backend|@domain>,<orgname>
        org.auth.1 = LDAP,LDAP users
        org.auth.2 = LocalDB,Local users
        org.email.3 = @gmail.com,Gmail

    With with example configuration, permissions can be defined for:

    - All LDAP users
    - All local users
    - All Gmail users

#.  Update organization info into database using ``trac-admin`` command::

        trac-admin /var/www/trac/projects/home mp user update org

.. _import-old-files:

Migrating to Files Downloads
============================

If the existing instance of MultiProject would not have Files Downloads, there are some extra
tasks needed to be done.

#.  Update the Apache configuration for the webdav by adding the PythonCleanupHandler
    directive::

        <LocationMatch "^/dav/.+">
            PythonHeaderParserHandler multiproject.core.auth.mod_python_access.webdav
            PythonCleanupHandler multiproject.core.auth.mod_python_access.webdav
            PythonOption realm "MultiProject webdav"
            Allow from all
        </LocationMatch>

#.  Disable the DownloadsGlue components by default. Disable FilesWebAdmin in case you don't
    want users to be able to change the downloads dir::

        [components]
        multiproject.project.files.downloadsglue.downloadsglue = disabled
        multiproject.project.files.admin.fileswebadmin = disabled

#.  Move [multiproject] sys_dav_root and url_dav_path keys into [multiproject-files],
    and remove leading slash from url_dav_path, if they are set in project.ini.
    Also, you might want to update the configurations for [multiproject] public_auth_group,
    public_auth_group, anon_forbidden_actions, and default_groups so that the
    WEBDAV_* and DOWNLOADS_* permissions are renamed to FILES_* and FILES_DOWNLOADS_*
    permissions and the proper permissions are given by default and revoked from
    anonymous user.

#.  Upgrade all existing project environments with MultiProject global upgrade::

        trac-admin /var/www/trac/projects/home mp upgrade do

#.  Finally, If an existing instance of MultiProject was with TracDownloads (see
    :ref:`install-plugin-downloads`) enabled, you need to run the following
    trac-admin commands as a web server user::

        # To create default downloads folder for all projects (except "home")
        trac-admin /var/www/trac/projects/home mp run files download create
        # To import existing downloads files from TracAdmin
        # and to enable DownloadsGlue component
        trac-admin /var/www/trac/projects/home mp run files import

#.  The TracDownloads is currently not compatible with Files Downloads feature, since
    :class:`multiproject.project.files.wiki.ProjectDownloadsWiki` component overrides
    the TracDownloads links and
    :class:`multiproject.project.files.downloadsglue.DownloadsGlue`
    overrides the TracDownloads macros. Thus, it should be disabled, if it is installed::

        [components]
        tracdownloads.* = disabled
