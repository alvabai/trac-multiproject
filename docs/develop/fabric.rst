.. _develop-fabric:

============
Using Fabric
============
Fabric_ (fab) is a tool for automating remote (and local) run tasks. In this project Fabric is used as a
helper tool for common development related tasks. In MultiProject case, deployment with Fabric tasks run
the final deployment task with a shell script called ``deploy.sh``, which is located in the ``scripts/``
sub directory in the MultiProject Plugin git repository, see :ref:`develop-source`. This script is not
applicable for creating a clean install, from the scratch, so :ref:`install` steps need to be
referred from time to time to complete certain tasks.

.. contents::
   :local:

.. _develop-fabric-configuration:

Fabric Configuration
====================
For Fabric tasks to run correctly, it is essential to configure some setup sections for the tasks to rely on.
MultiProject plugin offers a template file for this, on the top level in repository, called
``fabfile.example.ini``. You should copy this file into one of the following locations, or into a location
pointed by environment variable ``$FABFILEINI``::

    ~/.fabfile.ini
    /etc/fabfile.ini
    ./fabfile.ini

While changing contents of the fabric configuration, it should be noted that paths like ``hgweb_path``,
``git_bin_path``, ``git_core_path`` and ``trac_root`` are set correctly. These will be the most important
values for building configurations. Additional important things include ``db_user``, ``db_password`` and
``db_host``. If these are not correct, then the access to database will fail on all project environments.

Example configuration:

.. literalinclude:: ../../fabfile.example.ini
    :language: ini

Fabric tasks use a shell script for deployment. Unfortunately the deployment only supports updating existing
installation, and only if the installation is done in a very specific way. This way include a custom ``.pth``
file to be installed into python dist- or site-packages directory.

For example, in a configuration, where the project files would be installed into ``/var/www/trac``, this setup
would require a sub dir dist under the ``trac_root``. There, the ``deploy.sh`` script would create a sub dir
based on timestamp of the installation, and point a symbolic link ``current`` into the time stamped directory.

.. note::

    ``deploy.sh`` takes it's configuration from file ``/etc/trac/env.sh``, which might conflict with
    the values in your ``fabfile.ini``.

The ``deploy.sh`` script also installs a ``dist.pth`` file into the current directory, which points into the
current eggs installed with the script. For this to do any good, there needs to be a symbolic link from python
lib dir into this file, so ensure one is done::

    sudo ln -s /var/www/trac/dist/current/dist.pth /usr/local/lib/python2.7/dist-packages/dist.pth

.. note::

    Change python version and link location directory based on the system configuration.


Fabric roles
============
.. todo::

    Explain this in some sensible way

Running a single role with a specific task::

    fab -R example-fe system.restart_apache

List of roles can be seen by running::

    fab help


.. _develop-fabric-building:

Building with Fabric
====================
With fabric, building is just a simple task::

    fab dist.build:ext="true"

The results of the build will be available in the ``dist/`` directory, in requested package formats.
The task supports more build formats, possiblity to build the documentation and download and patch the
external dependencies relevant to MultiProject plugin. For more information about these options see
``fab -d dist.build``. If doing first install, the option ``ext="true"`` is a must, to include external
plugins in the installation process.

Content of the package contains the MultiProject code, theme, configurations, scripts and
following plugins::

    multiproject-all-1.0.0/plugins/Genshi-0.6.1dev_r1135-py2.7.egg
    multiproject-all-1.0.0/plugins/BatchModify-0.8.0_trac0.12-py2.7.egg
    multiproject-all-1.0.0/plugins/TracGit-0.12.0.5dev-py2.7.egg
    multiproject-all-1.0.0/plugins/MultiProject-1.1.7-py2.7.egg
    multiproject-all-1.0.0/plugins/gitosis-0.2-py2.7.egg
    multiproject-all-1.0.0/plugins/TracXMLRPC-1.1.0_r8688-py2.7.egg
    multiproject-all-1.0.0/plugins/TracCustomFieldAdmin-0.2.8_r11265-py2.7.egg
    multiproject-all-1.0.0/plugins/TracDownloads-0.3.mppv-py2.7.egg
    multiproject-all-1.0.0/plugins/TracDiscussion-0.8-py2.7.egg
    multiproject-all-1.0.0/plugins/Trac-0.12.4-py2.7.egg
    multiproject-all-1.0.0/plugins/TracMercurial-0.12.0.23dev_r9953-py2.7.egg
    multiproject-all-1.0.0/plugins/TracMasterTickets-3.0.2-py2.7.egg
    multiproject-all-1.0.0/plugins/Tracchildtickets-1.0.5-py2.7.egg


.. _develop-fabric-installation:

Installation using Fabric
-------------------------
It is possible to configure Fabric to do the deployment in the target environment. This works well for
update process, but not all that well with clean installation. However, if something like the following
is present in ``~/.fabfile.ini``, then the installation is much easier:

.. code-block:: ini

    [setup:localhost]
    trac_root = /var/www/trac
    fe_hosts = localhost
    mc_hosts = localhost
    db_hosts = localhost
    domain_name = localhost
    webserver_user = www-data
    webserver_group = www-data
    db_user = tracuser
    db_password = password

.. note::

    On target environment, as described in :ref:`install` ``/etc/trac/env.sh`` needs to
    be set to compliment the configuration.

By running::

    fab -H localhost dist.deploy:package="dist/multiproject-all-*.tar.gz",opts="--theme --activate"

Fabric will, over ssh, copy the package in place, and create few necessary symlinks for python to find and
lay the eggs that are required for MultiProject installation. The results will be installed into
``/var/www/trac/dist`` directory, if using the example configuration.

Typical example of this directory is something of the sorts::

    20120117134959/
        dist.pth
        egg/
            BatchModify.egg/
            TracMultiProject.egg/
            TracDiscussion.egg/
            TracDownloads.egg/
        scripts/
        theme/
    current -> 20120117134959/

In addition to the single fabric command, it is essential to install also the eggs that are not included
in the installation directory. The eggs can be installed with following commands::

    fab -H localhost dist.deploy:package="dist/gitosis-0.2.tar.gz"
    fab -H localhost dist.deploy:package="dist/TracMercurial-0.12.0.23dev-r9953.tar.gz"
    fab -H localhost dist.deploy:package="dist/Trac-0.12.4.tar.gz"
    fab -H localhost dist.deploy:package="dist/TracCustomFieldAdmin-0.2.8-r11265.tar.gz"
    fab -H localhost dist.deploy:package="dist/TracGit-0.12.0.5dev.tar.gz"
    fab -H localhost dist.deploy:package="dist/TracXMLRPC-1.1.0-r8688.tar.gz"
    fab -H localhost dist.deploy:package="dist/Genshi-0.6.1dev-r1135.tar.gz"
    fab -H localhost dist.deploy:package="dist/TracMasterTickets-3.0.2.tar.gz"

After this configurations need to be installed into the target environment as described in
:ref:`install-plugin`. This is needed before continuing into :ref:`install-server-home`.
