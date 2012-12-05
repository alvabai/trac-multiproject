.. _install-server:

========================
Environment installation
========================
This section describes how to setup MultiProject environment manually.

.. contents::
   :local:

.. _install-server-dep:

Install dependencies
====================
Following applications, libraries and modules are to be installed on MultiProject powered Trac setup.
Some of them are feature specific and can be leaved out, depending on setup. In this documentation, all
the features are to be enabled.

.. note::

    - **Running Ubuntu?** Good. These instructions are written for `Ubuntu Server <http://www.ubuntu.com/download/server/download>`_,
      meaning the name of packages and commands may vary if using any other distribution.

    - **Running RedHat/CentOS?** There is a `EPEL (Extra Packages for Enterprise Linux) <http://fedoraproject.org/wiki/EPEL>`_
      that contains many of the required packages.

    - **Developer?** For building/developing the plugin, you'll also need additional tools and modules
      described in :ref:`setting up development environment <develop-env>`.
      For adventurous and for environments where system packages are too old, there are some
      :ref:`instructions how to build packages from sources <develop-build>`

#.  Install packages:

    In Ubuntu::

        sudo apt-get install apache2-mpm-prefork libapache2-mod-python libapache2-svn \
        wget git subversion python python-dev python-pip python-mysqldb python-subversion \
        mysql-client mysql-server unzip libldap2-dev libsasl2-dev memcached libssl0.9.8 \
        python-memcache python-ldap

    In CentOS::

        sudo yum install httpd mod_dav_svn mod_python mod_ssl git subversion mercurial memcached \
        mysql mysql-server python-ldap python-imaging python-setuptools python-memcached
        compat-openldap openssl098e

#.  Install pip_ python package installer::

         curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python

#.  Install additional python modules:

    .. note::

        It is up to you whether you want to install python modules from operating system repository or from
        Python package index (http://pypi.python.org) using pip_ or easy_install_. However, if module contains
        some c -code functionality, you'll also a set of development packages and tools to be installed. Moreover,
        some of the system packages may be outdated. The required versions for the modules are:

        - SQLAlchemy >=0.7.x
        - Memcache >= 1.4x
        - LDAP >= 2.3.x

        Which you can install with command::

            sudo pip install python-ldap sqlalchemy pygments python-memcached

#.  Install Genshi:

    Genshi is the base for Trac's HTML generation system. MultiProject depends on a 0.6.x version::

        sudo pip install http://svn.edgewall.org/repos/genshi/branches/stable/0.6.x/

#.  Patch and install Trac:

    Trac is patched somewhat by MultiProject, to allow childtickets a better integration, amongst other things.
    To patch, build and install Trac::

        wget http://ftp.edgewall.com/pub/trac/Trac-0.12.1.tar.gz
        tar -xzf Trac-0.12.1.tar.gz
        cd Trac-0.12.1/
        patch -p0 --ignore-whitespace < ../ext/patches/trac/*.patch
        sudo python setup.py install
        cd -

#.  Install MultiProject:

    Install MultiProject plugin already at this point, as it is being widely used by the tools and configurations
    used below::

        sudo easy_install -Z TracMultiProject*.egg

#.  Install and enable Apache modules:

    The default Apache configuration file delivered with the package requires following modules to be enabled.
    Either modify the Apache configuration or enable modules with command::

        sudo a2enmod expires
        sudo a2enmod dav
        sudo a2enmod dav_fs
        sudo a2enmod ssl


.. _install-server-dir:

Prepare files and folders
=========================
MultiProject setup is mainly (and by default) located under ``/var/www/trac`` folder. In addition, there
are configuration files for used services like Apache, MySQL etc.

#.  Create filesystem structure::

        sudo mkdir -p /var/www/trac/analytics
        sudo mkdir -p /var/www/trac/archives
        sudo mkdir -p /var/www/trac/config
        sudo mkdir -p /var/www/trac/dist
        sudo mkdir -p /var/www/trac/downloads
        sudo mkdir -p /var/www/trac/hgweb
        sudo mkdir -p /var/www/trac/logs
        sudo mkdir -p /var/www/trac/projects
        sudo mkdir -p /var/www/trac/repositories
        sudo mkdir -p /var/www/trac/results
        sudo mkdir -p /var/www/trac/themes
        sudo mkdir -p /var/www/trac/webdav
        sudo mkdir -p /var/www/trac/scripts

        # Links from default locations
        sudo ln -s /var/www/trac/logs /var/log/trac
        sudo ln -s /var/www/trac/config /etc/trac
        sudo ln -s /usr/lib/python2.6/site-packages/trac/htdocs/ /var/www/trac/htdocs

#.  Set filesystem ownership to web server (see ``/etc/apache2/envvars`` for user and group value)::

        sudo chown -R www-data.www-data /var/www/trac

    .. important::

        .. index:: selinux

        Using SELinux? Change the policy as well::

            sudo chcon -R -t httpd_sys_content_t /var/www/trac

        See also additional documentation from Trac project site:
        http://trac.edgewall.org/wiki/TracWithSeLinux

#.  Copy default configuration from MultiProject package::

        sudo cp etc/trac/* /var/www/config/


.. _install-server-db:

Prepare database
================
MultiProject setup requires several separate databases: one for each project + one central database + one optional
database for analytics. Thus, you may end up databases as follows:

- trac_admin (shared by all of the projects)
- trac_analytics (needed only for statistics)
- projectx
- projecty
- projectz
- etc.

Follow the steps to create databases:

#.  Secure MySQL server

    - Run ``/usr/bin/mysql_secure_installation`` to set sane defaults for the MySQL server
    - Listen only required addresses by setting in ``/etc/my.cnf``::

        [mysqld]
        bind-address=127.0.0.1

    - Restart MySQL server::

        /etc/init.d/mysqld restart

#.  Create database user specific for the service. This user is used accessing both administrative databases as well
    as all the project databases::

        sudo mysql -u root -p
        mysql> GRANT ALL ON *.* TO 'tracuser'@'%' IDENTIFIED BY 'password';
        mysql> FLUSH PRIVILEGES;
        mysql> \q

    .. important::

        Because of fixed user information in database procedures, the user needs to be able to access database from
        all the hosts (``%``). This is known issue are we're working on getting rid of DB procedures and this limitation.


#.  Initialize database with database dump

    MultiProject has quite a few databases it requires. Fortunately, the so called empty database dump offers a nice
    starting point. The empty database dump is in the source repository: ``etc/templates/empty_database.sql``.
    This can be installed with::

        mysql -u root -p < etc/mysql/empty_database.sql

    .. warning::

        Do not use the database dump when you already have data in the database. This will clear all related
        MultiProject data. If you want to migrate existing database, see instruction from  :ref:`usage-update`

#.  Migrate database to latest schema

    The ``empty_database.sql`` contains the initial database structure and it needs to be migrated to latest
    schema using provided update script.

    Run the ``scripts/update.py`` found from package to list the available updates::

        sudo python ./scripts/update.py

    Example output (two migrations available)::

        STATUS      MIGRATION
        ---------------------------------------------------------------
        installed : 20110906120000_authentication_method_datatype
        installed : 20111207083300_wiki_start_time_to_utimestamp
        new       : 20120209130000_user_created
        new       : 20120210150000_project_events


        To install migrations
            python update.py --update=[target_migration_name]

    To migrate to latest version, provide the latest migration name as a parameter::

        python update.py --update=20120210150000_project_events

    .. tip::

        Whenever upgrading the database, :ref:`take backup from database <usage-backup-db>` first.


.. _install-apache:

.. _apache-configuration:

Setup web server
================
Apache is the suggested web server for running the Trac setup. This is also because MultiProject environment
takes advantage from some of the Apache modules.

There are two configuration files for Apache setup in MultiProject version control. These are
``multiproject.conf`` and ``multiproject-access.conf``. ``multiproject.conf`` contains values values
for ``mod_python``, few redirects, locations where to seek static resources and some other, rather
common apache configuration values. ``multiproject-access.conf`` contains handler configuration for
webdav, xmlrc, svn, git and mercurial. These files are present in ``etc/templates/httpd/`` sub dir on
the MultiProject plugin version control.

#.  **Copy default configuration** files from package and link them::

        cp etc/httpd/conf.d/* /var/www/trac/config/
        ln -s /var/www/trac/config/multiproject.conf /etc/apache2/conf.d/multiproject.conf
        ln -s /var/www/trac/config/multiproject-access.conf /etc/apache2/conf.d/multiproject-access.conf

#.  Set :envvar:`HOME` variable in Apache startup script ``/etc/init.d/apache2``::

        export HOME=/var/www/trac

#.  **Optional: Enable SSL**

    SSL is often desired and a good idea to take into use, not least for the user authentications.

    #.  Enable Apache module ``mod_ssl``::

            sudo a2enmod ssl

    #.  Create certificate (or use existing one)::

            sudo make-ssl-cert /usr/share/ssl-cert/ssleay.cnf \
            /var/trac/config/your-certificate.key

            sudo openssl req -new -key /var/trac/config/your-certificate.key \
            -out /var/trac/config/your-certificate.csr

        .. tip::

            In CentOS you can use ``genkey`` instead (found in ``crypto-utils`` package)::

                sudo yum install mod_ssl crypto-utils
                sudo genkey hostname

            See `documentation for details <http://www.centos.org/docs/5/html/Deployment_Guide-en-US/s1-httpd-secure-server.html>`_

    #.  Optional: Self-sign the certificate::

            sudo openssl x509 -req -days 365 \
            -in /var/www/trac/config/your-certificate.csr \
            -signkey /var/www/trac/config/your-certificate.key \
            -out /var/www/trac/config/your-certificate.crt

    #.  Modify Apache configuration as follows (replace ``localhost`` with correct domain name and certificate key):

        .. code-block:: apache

            <VirtualHost *:80>
                SetEnv HTTPS 1
                # NOTE: Always redirect http -> https
                RedirectMatch 302 (/.*) https://localhost$1
            </VirtualHost>

            <VirtualHost _default_:443>
                SSLEngine on
                # TODO: Set correct path
                SSLCertificateKeyFile    /var/www/trac/config/your-certificate.key
                SSLCertificateFile       /var/www/trac/config/your-certificate.crt
                SSLProtocol -ALL +SSLv3 +TLSv1
                SSLHonorCipherOrder On
                SSLCipherSuite RC4-SHA:HIGH:!ADH
            </VirtualHost>

            <LocationMatch "^/?$">
                # NOTE: redirect / -> /home
                Redirect / https://localhost/home
            </LocationMatch>

    #.  Change default scheme in ``/etc/trac/project.ini``:

        .. code-block:: ini

            [multiproject]
            default_http_scheme=https


    .. tip::

        For further information about SSL, refer little tutorial found in
        http://www.akadia.com/services/ssh_test_certificate.html

#.  **Optional: Enable WebDAV**

    WebDAV, is a service that allows hosting of a mountable filesystem. With MultiProject plugin, WebDAV is
    accessible for all projects and it's access can be configured via trac (and MultiProject extensions to it)
    permissions. Users and project admins are able to access and upload files via browser, MultiProject offers
    a trac plugin for this.

    #.  Enable the WebDAV in Apache:

        .. code-block:: bash

            sudo a2enmod dav
            sudo a2enmod dav_fs
            sudo service apache2 restart

    #.  Configure WebDAV root to match the environment setup:

        .. code-block:: ini

            [multiproject-files]
            # Dav root directory. Usually <trac home>/webdav
            sys_dav_root = /var/www/trac/webdav

    #.  Configure apache to use custom handlers for dav. MultiProject defines this into
        ``/etc/apache2/conf.d/multiproject-access.conf``:

        .. code-block:: apache

            # Set basic settings for SCM and DAV
            <LocationMatch "^/(git|hg|dav|svn)/.+">
              SetHandler None
              PythonOption auth_anonymous true
              Order allow,deny
              Allow from all
            </LocationMatch>

            # Prevent access for root
            <LocationMatch "^/dav/">
              Order deny,allow
              Deny from all
            </LocationMatch>

            # Allow access for subfolders (overrides the root match rule)
            <LocationMatch "^/dav/.+">
              PythonHeaderParserHandler multiproject.core.auth.mod_python_access.webdav
              PythonCleanupHandler multiproject.core.auth.mod_python_access.webdav
              PythonOption realm "MultiProject webdav"
              Allow from all
            </LocationMatch>

    #.  Prevent HTML content being rendered:

        If the installation is publicly accessible, HTML rendering must be disallowed to prevent
        potential CSRF abuse.

        .. code-block:: bash

            sudo a2enmod headers

        Include following rule with in WebDAV directory definition.

        .. code-block:: apache

            # Prevent HTML content being rendered in browser (CSRF)
            <FilesMatch "\.(?i:html|htm)$">
              Header set Content-Disposition attachment
            </FilesMatch>

.. _install-server-home:

Create home project
===================
MultiProject setup requires a special Trac project, which will have a different components enabled than the
actual projects. This special project is referred with the name ``home``

#.  Create home project with ``trac-admin`` tool::

        sudo trac-admin /var/www/trac/projects/home initenv home \
        mysql://tracuser:password@localhost/home --inherit=/var/www/trac/config/project.ini

    Replace ``tracuser``, ``password`` and ``localhost`` with the configuration used for the site's mysql
    server.

#.  Modify home configuration file (``home/conf/trac.ini``) to have following values (or overwrite the config
    with the template found in``etc/templates/trac/home.ini``):

    .. literalinclude:: ../../etc/templates/trac/home.ini
       :language: ini

#.  Verify setup

    Go ahead and open browser to ensure the steps taken so far are ok. Start webserver and
    open web browser::

        http://localhost/home


If no errors are shown, go head and continue to :ref:`next chapter <install-plugin>`.
