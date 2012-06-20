.. _develop-env:

=======================
Development environment
=======================
This chapter describes how to get started with the MultiProject development.

.. note::

   For running the service, only Linux is currently support. Therefore, if developing
   under Windows, run the service in virtual environment and mount the sources in local
   drive.

.. contents::
   :local:


Prerequisites
=============
Following tools and libraries are needed for the development.


#.  Install system packages::

        sudo apt-get install apache2-mpm-prefork libapache2-mod-python libapache2-svn \
        wget git subversion python python-dev python-pip python-mysqldb python-subversion \
        mysql-client mysql-server unzip libldap2-dev libsasl2-dev


#.  Install python modules::

        sudo pip install Fabric Sphinx requests paramiko yuicompressor stdeb pyinotify

#.  Install your favourite editor, for example:

    - pycharm: http://www.jetbrains.com/pycharm/
    - vim: http://vim.org
    - emacs: http://www.gnu.org/software/emacs/

.. _develop-source:
.. _get-source:

Getting the sources
===================
MultiProject is hosted in https://projects.developer.nokia.com, in a git repository. If the source
has already been cloned via git, then this information might be reduntant. However,
the latest source code can be obtained by::

    git clone https://projects.developer.nokia.com/git/multiproject.git MultiProjectPlugin

Branch used for development is called ``develop``. So if latest, however potentially unstable, version
of the software is required, checkout the development branch::

    cd MultiProjectPlugin
    git checkout develop
    cd -


Building
========
Assumption in these steps is that sources have been fetched for MultiProject plugin. See :ref:`develop-source`.
Starting point before doing any of the installation is in the directory where the cloned MultiProject plugin
resides, each step begins by doing a cd into that directory. These steps will also install all eggs into system
wide dist-, or site-packages directory. On newer ubuntu releases the place for eggs will be
``/usr/local/lib/python2.7/dist-packages``.


#.  Clean up old build results

    Focusing on cleaning the results from any previous builds. Often a good idea to do before trying to do new
    installation::

        sudo rm -rf trac-genshi
        sudo rm -rf Trac-0.12.1*
        sudo rm -rf coderanger-trac-mastertickets*
        sudo rm trac-mastertickets.tar.gz
        sudo rm -rf trac-xmlrpc
        sudo rm -rf trac-customfieldadmin
        sudo rm trac-git.tar.gz
        sudo rm -rf hvr-trac-git-plugin-*
        sudo rm gitosis.tar.gz
        sudo rm -rf gitosis



.. _repository-contents:

Repository contents
===================
Project repository is structured as follows:

.. code-block:: bash

    build/                  # Temp directory where all the building is done
    dist/                   # Temp directory where all packages are built to
    docs/                   # Text based documentation and configuration files, powered by Sphinx.
    etc/
      templates/            # Configuration templates.
        empty_database.sql  # Empty database for **new** setups
      httpd/                # Example Apache configuration files
      trac/                 # Trac, VCS access and MultiProject environment configurations.
    scripts/                # Scripts and small apps used for/by the app.
      fabric/               # Fabric tasks for building, distributing and deploying.
    cron/                   # Cron tasks for analytics, ssh key syncs, timeline refresh etc.
      hooks                 # Some common hooks for VCS.
    tests/                  # Automated web tests, powered by Selenium.
    plugins/                # Plugin(s), each on their own directory.
      multiproject/         # MultiProject plugin (along with related plugins)
        multiproject/       # The actual MultiProject plugin source.
          core/             # A standalone utility library used by the plugin and it's support scripts code.
          project/          # Common project related plugins.
          home/             # The administration project related code.
          common/           # Common plugin related code.
          tests/            # Unit tests for the whole project.
        database/           # Some reduntant database related dumps, which are somewhat out of date.
    themes/                 # Themes folder.
      default/              # Default theme delivered along with the MultiProject -plugin.
    ext/                    # External modules and plugins modified for/by the project.
      libs/                 # External libraries.
      patches/              # Patches written on top of 3rd party plugins/libs.
      plugins/              # External Trac plugins, modified by the project
    fabfile.py              # The main project script for building etc.
    fabfile.example.ini     # Configuration template for Fabric tasks.
