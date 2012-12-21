.. _develop-env:

=======================
Development environment
=======================
This chapter describes how to get started with the MultiProject development.

.. note::

    For running the service, only Linux is currently support. Therefore, if developing
    under Windows, run the service in virtual environment and mount the sources in local
    drive.

Setting up the development environment is not much different from the
:ref:`setting up the production <install-server>`. One notable difference is the installation of the
developed modules::

    # Use this: Create link so source code
    python setup.py develop

    # Do **not** use this
    python setup.py install

Also, to make Apache reload sources on every request set following in ``apache2.conf``::

        <IfModule mpm_prefork_module>
            StartServers          5
            MinSpareServers       5
            MaxSpareServers      10
            MaxClients          150
            # For production
            #MaxRequestsPerChild   100
            # For development
            MaxRequestsPerChild   1
        </IfModule>


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

Building
========
All the commands are run using the Fabric_ script.

#.  Create base directory for the projects::

        mkdir ~/projects

#.  Retrieve sources::

        cd ~/projects
        git clone https://collab.nokia.com/git/CQDE.git cqde
        git clone https://projects.developer.nokia.com/git/multiproject.git multiproject

    .. tip::

        You can use ``.netrc`` file to store HTTP authentication information::

            machine collab.nokia.com
                login myaccount
                password mypassword

            machine projects.developer.nokia.com
                login myssoaccount
                password mypassword

#.  Retrieve external components (needed only if developed)::

        git clone https://projects.developer.nokia.com/git/tracdiscussion.git tracdiscussion
        git clone https://projects.developer.nokia.com/git/childtickets.git childtickets
        git clone https://projects.developer.nokia.com/git/batchmodify.git batchmodify

#.  Fetch, patch and build packages::

        cd multiproject
        fab dist.build:ext=all

    This will build ``MultiProject``, fetch dependencies and built them as well. Outcome will be
    place in ``dist`` -directory

    .. tip::

        For more instructions for ``fab dist.build`` run::

            fab -d dist.build

#.  Install non-developed packages::

        cd dist
        easy_install -Z BatchModify-*.egg
        easy_install -Z Genshi-*.egg
        pip install gitosis-*.tar.gz
        easy_install -Z Trac-*.egg
        easy_install -Z Tracchildtickets-*.egg
        easy_install -Z TracCustomFieldAdmin-*.egg
        easy_install -Z TracDiscussion-*.egg
        easy_install -Z TracGit-*.egg
        easy_install -Z TracMasterTickets-*.egg
        easy_install -Z TracMercurial-*.egg
        easy_install -Z TracXMLRPC-*.egg

#.  Install from sources::

        cd ~/projects/multiproject/plugins/multiproject
        python setup.py develop

        cd ~/projects/cqde/nokia/plugins/dnc
        python setup.py develop

        cd ~/projects/cqde/nokia/plugins/nokia
        python setup.py develop

#.  Setup and configure server

    Follow the starting from :ref:`install-server-dir`

.. _develop-doc:

Building documentation
======================
The project documentation is written using Sphinx_ maintained in version control,
under ``docs`` directory. Build documentation with command::

    fab dist.builddoc

.. tip::

    When you're writing the documentation, you can use ``autobuild`` that builds
    the documentation whenever the files are changed::

        fab dist.autobuild


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
