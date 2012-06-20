
.. _usage-update:

========
Updating
========
This chapter describes how to update existing Multiproject setup.

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

To run migration step::

    python update.py --update=20120210150000_project_events


.. _usage-backup-db:

Backup database
===============
It is a good practice to take backups from databases regularly, and especially before :ref:`migrating database <usage-update-db>`.
Because setup consists from multiple database and routines, the MySQL database backup is taken with command::

    mysqldump --all-databases --routines -u root -p > multiproject-`date +%Y%m%d-%H%M%S`.mysqldump.sql

To restore the database dump, run::

    mysql -u root < multiproject-20120405.mysql.sql

