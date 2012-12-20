.. _install-extra:

==============
Extra features
==============
This chapter describes how to setup the optional/additional features to your MultiProject setup.
Install the components that you need.

.. contents::
   :local:

.. _install-extra-analytics:

Statistics
==========
MultiProject plugin comes with optional analytics service, where different kind of statistics can be
pulled from projects and it's usage. Follow the steps to enable it in your setup:

.. todo:: Write about MP analytics


#.  Create background tasks as cron jobs::

        sudo -u www-data crontab -e

    Contents::

        # Read event log from log to database (Frequently)
        0,6,12,18,24,30,36,42,48,54 * * * * python /var/www/trac/scripts/analytics/run_event_etl.py

        # Refresh summary data (Every hour)
        10 * * * * python /var/www/trac/scripts/analytics/summarize.py

        # Rotate partitions so that the analytics tables have partitions for new data
        # to be inserted (From time to time)
        0 4 * * * python /var/www/trac/scripts/analytics/rotate_partitions.py

        # Clone dimension data from operational database (Every day)
        0 4 * * * python /var/www/trac/scripts/analytics/dimension_sync.py

#.  Run rotate_partitions.py and dimension_sync.py manually. Repeat if "Out of range" warnings are displayed::

        python /var/www/trac/scripts/analytics/dimension_sync.py
        python /storage/trac/scripts/analytics/rotate_partitions.py


.. _install-extra-messaging:

Instant messages
================
Multiproject plugin comes with optional messaging service, allowing users to send messages to each other, similar
to chat or Facebook_. Feature comes with additional dependencies, but it's worth of effort.

#.  Install Juggernaut service (for storing and sending notifications)

    -   Install Redis_ database (requires development tools like ``make`` and ``gcc``)::

            wget http://redis.googlecode.com/files/redis-2.4.14.tar.gz
            tar xzf redis-2.4.14.tar.gz
            cd redis-2.4.14
            make
            sudo make install
            sudo mkdir /etc/redis
            sudo cp redis.conf /etc/redis
            sudo cp utils/redis_init_script /etc/init.d/redis

        .. tip::

            You can also install it via OS package manager, but at least Redis version 2.4.x is needed.
            There exist some ready-made init script in the Internet.
            For CentOS:

            https://raw.github.com/gist/257849/9f1e627e0b7dbe68882fa2b7bdb1b2b263522004/redis-server

            Do note how ``make install`` puts ``redis-server`` on ``/usr/local/bin``, not ``/usr/local/sbin``.

    -   Modify Redis init script: ``/etc/init.d/redis``::

             PIDFILE=/var/run/redis.pid
             CONF="/etc/redis/redis.conf"

    -   Configure Redis_ (suggested values listed): ``sudo vim /etc/redis/redis.conf``::

            daemonize = yes
            bind 127.0.0.1
            loglevel notice

    -   Start Redis_ database service::

            sudo /etc/init.d/redis-server start

    -   Install python redis module::

            sudo pip install redis

    -   Install `Node.js` and NPM_:

        - On CentOS (see http://nodejs.tchol.org/)::

            wget http://nodejs.tchol.org/repocfg/el/nodejs-stable-release.noarch.rpm
            sudo yum localinstall --nogpgcheck nodejs-stable-release.noarch.rpm
            sudo yum install nodejs npm
            sudo ln -s /usr/bin/nodejs /usr/bin/node

            # Alternatively, download the the *.rpm packages from http://nodejs.tchol.org/
            # and run yum localinstall --nogpgcheck *.rpm

        - On Ubuntu (or build from source)::

            sudo add-apt-repository ppa:chris-lea/node.js
            sudo apt-get install nodejs npm

        - From source (see https://github.com/joyent/node/wiki/Installation)::

            wget http://nodejs.org/dist/v0.6.19/node-v0.6.19.tar.gz
            tar -xzf node-v0.6.19.tar.gz
            cd node-v0.6.19/
            ./configure
            make
            sudo make install

            # Install NPM
            curl http://npmjs.org/install.sh | sh

    -   Install Forever_ daemon (for running Juggernaut_ `Node.js`_ application)::

            sudo npm install -g forever

        .. important::

            Forever needs to be installed with option ``-g``. Otherwise it will give an error::

                node.js:134
                throw e; // process.nextTick error, or 'error' event on first tick
                ^
                Error: Cannot find module '../build/default/daemon'

        .. tip::

            NPM_ installs modules directly from the internet. If the connection is prohibited,
            you can pack the packages locally, copy them to server and install from pack::

                # Locally
                npm pack juggernaut forever
                scp *.tgz productionserver.com:

                # At productionserver
                npm install -g *.tgz

        .. note::

            By default, NPM_ install modules to ``/usr/lib/node_modules``

    -   Install Juggernaut_::

            sudo npm install -g juggernaut

    -   Add SSL support in Juggernaut (optional)

        The suggested deployment model is to terminate SSL connections to frontend and proxy the requests
        as HTTP to Juggernaut service. However, if websocket connections are/can be allowed, the secure
        connections should be used. Juggernaut runs in secure mode if the ``keys`` folder exists with
        suitable ``.pem`` files in it:

        .. code-block:: bash

            mkdir /usr/lib/node_modules/juggernaut/lib/juggernaut/keys
            cd keys
            openssl genrsa -out privatekey.pem 1024
            openssl req -new -key privatekey.pem -out certrequest.csr
            openssl x509 -req -in certrequest.csr -signkey privatekey.pem -out certificate.pem

    -   Copy service script from ``etc/init.d/juggernaut.<type>`` to ``/etc/init.d/juggernaut`` (``juggernaut.upstart`` for Ubuntu
        and ``juggernaut.init`` for CentOS and RedHat)::

            sudo cp etc/init.d/juggernaut.upstart /etc/init.d/juggernaut
            sudo chmod +x /etc/init.d/juggernaut

    -   Adjust socket.io parameters (optional):

        Juggernaut does not have an easy way to adjust socket.io server parameters. Thus,
        modify the ``/usr/lib/node_modules/juggernaut/lib/juggernaut/server.js`` directly:

        .. code-block:: javascript

            this.io = io.listen(this.httpServer);
            this.io.sockets.on("connection", function(stream){ Connection.inst(stream) });
            // ^-- these lines are only as reference where to place changes show below

            // Set/adjust socket.io server settings as needed
            // See https://github.com/LearnBoost/Socket.IO/wiki/Configuring-Socket.IO for reference
            this.io.set('polling duration', 30);            // Keep connection open for 30 seconds
            this.io.enable('browser client minification');  // send minified client
            this.io.enable('browser client etag');          // apply etag caching logic based on version number
            this.io.enable('browser client gzip');          // gzip the file

    -   Start services and check status::

            sudo service redis-server start
            sudo service juggernaut start
            sudo service juggernaut status

    -   Expose Juggernaut_ service using Apache proxy:

        .. code-block:: apacheconf

                # Load proxy modules
                LoadModule  proxy_module         modules/mod_proxy.so
                LoadModule  proxy_http_module    modules/mod_proxy_http.so
                SSLProxyEngine on

                # Proxy configuration for Juggernaut resources
                ProxyPass /application.js http://localhost:8080/application.js
                ProxyPassReverse /application.js http://localhost:8080/application.js
                ProxyPass /socket.io http://localhost:8080/socket.io
                ProxyPassReverse /socket.io https://localhost:8080/application.js

        .. important::

           Apache proxy does not support websocket connections. Thus, you can either:

           #. Open the Juggernaut port to firewall (or configure it to loadbalancer)
           #. Disable websocket connections in configuration (leaving out the ``websockets``)::

                juggernaut_transports = htmlfile, xhr-polling, jsonp-polling

#.  Enable required components in ``project.ini`` and configure Juggernaut:

    .. code-block:: ini

        [components]
        multiproject.common.notifications.* = enabled
        multiproject.common.messages.* = enabled

        [multiproject-messages]
        # Connection to Juggernaut service
        # Defaults to current host
        juggernaut_host =
        # Defaults current port
        juggernaut_port =
        # Defaults to current protocol
        juggernaut_secure =
        # Options: websockets, flashsocket, htmlfile, xhr-polling, jsonp-polling. Multiple values supported.
        # If empty, automatic selection is used
        # Example: juggernaut_transports = htmlfile, xhr-polling, jsonp-polling
        juggernaut_transports =
        # Placeholder/help wiki text to show in message box
        placeholder_text = === Messages ===
            This is the help text to show for the users in message box.

            - See WikiFormatting
            - See WikiMacros

            If empty, no message is shown. If not set, the component has default text to show.

        # Redis database
        redis_host = localhost
        redis_port = 6379

#.  Migrate the database (if not up-to-date)::

        python update.py --update=20120529090000_message_tables

#.  Set automatic purge for old messages (optional)

    Component comes with the Trac Admin command that removes old messages from the system::

        crontab -u www-data -l

        # Purge messages older than 30 days (run script weekly bases on every Sunday 0:00)
        0 0 * * 0 trac-admin /var/www/trac/projects/home/ mp message purge 30

    .. tip::

        If you're automatically removing messages from the system, be sure to communicate it to the users
        for example using the ``placeholder_text`` in configuration:

        .. code-block:: ini

            [multiproject-messages]
            placeholder_text = === Welcome to messages ===
                This is a secure instant messaging solution for you projects.

                '''NOTE''': Messages are automatically deleted after 30 days!



.. index:: performance

.. _install-extra-apache-static:

Apache for static files
=======================
Here are the instructions how to use Apache_ to serve static files:

- Create link to Trac htdocs::

    ln -s /usr/lib/python2.6/site-packages/trac/htdocs /var/www/htdocs

- Define alias in Trac configuration (``multiproject.conf``):

  .. code-block:: apacheconf

    Alias /htdocs/trac /var/www/htdocs
    <Directory /var/www/htdocs>
        # These rules are needed for caching static trac resources
        ExpiresActive On
        ExpiresByType image/* "access plus 1 week"
        ExpiresByType text/css "access plus 1 week"
        ExpiresByType text/js "access plus 1 week"
        FileETag INode MTime Size
        Options -Indexes
        Order allow,deny
        Allow from all
    </Directory>


.. _install-extra-rotate-log:

Rotate log files
================
Split log files into chunks using ``logrotate``:

- Copy ready-made ``logrotate`` configuration file from package::

    sudo cp etc/logrotate/* /etc/logrotate.d/

  .. literalinclude:: ../../etc/templates/logrotate/multiproject

- Test ``logrotate`` runs without errors::

    sudo logrotate -vf /etc/logrotate.d/multiproject

.. note::

    Apache server needs to be reloaded when the Apache logs are rotated: otherwise
    server will keep writing logs to rotated files. With logrotate this is
    done by using ``apache2 reload``.


.. _install-extra-memcache:

Memcache for caching
====================
It is highly suggested to install and use Memcache with the MultiProject.
Plugin works without it, but is slower.

- Install memcache server(s)::

    sudo apt-get install memcached

- Start service::

    sudo /etc/init.d/memcached start

- Set host to ``project.ini`` (config keys and default values shown below)::

    [multiproject]
    memcached_host = 127.0.0.1
    memcached_port = 11211
    memcached_enabled = true

  .. tip::

     You can provide multiple memcache servers separated with comma::

        memcached_host = 192.168.0.101,192.168.0.102

- Restart Apache servers on all frontends::

    sudo /etc/init.d/apache2 restart


.. _extra-zenoss:

Monitoring with Zenoss
======================
For monitoring the production environments, there are several solutions available. This section
summarizes how to setup Zenoss_ monitor for MultiProject environment. More thorough installation
instructions can be found from the Internet.

.. note::

    Because of Zenoss_ packages, the expected environment is CentOS 6.x (64bit)


Zenoss server
-------------

#.  Install MySQL_ 5.5 (5.1.x is not supported by Zenoss 4.x)::

        wget http://cdn.mysql.com/Downloads/MySQL-5.5/MySQL-client-5.5.27-1.linux2.6.x86_64.rpm
        wget http://cdn.mysql.com/Downloads/MySQL-5.5/MySQL-shared-5.5.27-1.linux2.6.x86_64.rpm
        wget http://cdn.mysql.com/Downloads/MySQL-5.5/MySQL-server-5.5.27-1.linux2.6.x86_64.rpm

        /etc/init.d/mysql start

        # Migrate existing databases if needed
        mysql_upgrade -u root -p

#.  Install python MySQL (needs to be compiled against the MySQL 5.5)::

        # Needed for MySQL-python installation
        wget http://cdn.mysql.com/Downloads/MySQL-5.5/MySQL-devel-5.5.27-1.linux2.6.x86_64.rpm
        pip install MySQL-python

#.  Install RabbitMQ_::

        wget http://www.rabbitmq.com/releases/rabbitmq-server/v2.8.4/rabbitmq-server-2.8.4-1.noarch.rpm
        wget http://dl.fedoraproject.org/pub/epel/6/x86_64/erlang-R14B-04.1.el6.x86_64.rpm
        yum localinstall rabbit
        /etc/init.d/rabbitmq-server start

#.  Install Java::

        wget -N -O jre-6u31-linux-x64-rpm.bin http://javadl.sun.com/webapps/download/AutoDL?BundleId=59622
        ./jre-6u31-linux-x64-rpm.bin
        yum localinstall jre*.rpm

#.  Install RRDtool 1.4.x::

        wget http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.2-2.el6.rf.x86_64.rpm
        yum localinstall rpmforge*.rpm
        yum -y --enablerepo='rpmforge*' install rrdtool-1.4.7

#.  Install Zenoss::

        wget http://sourceforge.net/projects/zenoss/files/zenoss-4.2/zenoss-4.2.0/zenoss-4.2.0.el6.x86_64.rpm
        wget http://sourceforge.net/projects/zenoss/files/zenpacks-4.2/zenpacks-4.2.0/zenoss-core-zenpacks-4.2.0.el6.x86_64.rpm
        yum -y --enablerepo='epel*' install zenoss-*.rpm

    Packages are installed at ``/opt/zenoss``.

#.  Configure Zenoss:

    - Set database host, username and password (``/opt/zenoss/etc/global.conf``)::

          zodb-host localhost
          zodb-admin-user root
          zodb-admin-password
          zep-host localhost
          zep-admin-user <username>
          zep-admin-password <password>

    - Limit access to localhost (``/opt/zenoss/etc/zope.conf``)::

          ip-address 127.0.0.1

          <http-server>
          address 9090
          </http-server>

#.  Start Zenoss::

        /etc/init.d/zenoss start

Monitored server
----------------
The information is read from server using SNMP_ (also SSH can be used, but with limited outcome).


#.  Install SNMP_::

        yum install snmpd

#.  Configure SNMP (``/etc/snmp/snmpd.conf``)::

        cp /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.backup
        vim /etc/snmp/snmpd.conf


        com2sec notConfigUser  default   randompasswordlikestring
        group   notConfigGroup v1        notConfigUser
        group   notConfigGroup v2c       notConfigUser

        view    systemview    included   .1
        view    systemview    included   .1.3.6.1.2.1.1
        view    systemview    included   .1.3.6.1.2.1.25.1.1

        access  notConfigGroup ""      any       noauth    exact  systemview none none

        com2sec readonly localhost       randompasswordlikestring

#.  Restart and check connection::

        /etc/init.d/snmpd restart
        snmpwalk -v2c -crandompasswordlikestring localhost:161 .1.3

    Expected outcome: long printout.


Zenoss usage
------------
Once again, more complete instructions can be found from Internet, but here are few pointers
to startup with Zenoss monitoring.


**Add new device**:
    - Nagivate: Infrastructure -> Icon (Monitor with plus): Add devices -> Add single device
    - Set IP address
    - Set device class: ``/Server/Linux``
    - Set Snmp community: ``randompasswordlikestring``

**Add plugins**:
    Plugins are called *zenpacks* in Zenoss and they can be found from: http://community.zenoss.org/community/zenpacks
    The documentation about the core documentation is located: http://community.zenoss.org/community/documentation/official_documentation/zenoss-extended-monitoring

    - Download ``py-2.6.egg`` file for Zenoss 4.x
    - IMPORTANT! Rename ``py-2.6.egg`` -> ``py-2.7.egg`` (Zenoss 4.x does give an error otherwise)
    - Navigate: Advanced -> ZenPacks -> Icon (Gear) -> Install ZenPack... -> Choose egg file
    - Navigate: Advanced -> Daemons -> zopectl -> Restart

    .. note::

        Package ``zenoss-core-zenpacks-4.2.0.el6.x86_64.rpm`` comes with built-in zenpacks, which can be found
        from ``/opt/zenoss/packs``. To install/enable them, install them from command line (at Zenoss server)::

            su zenoss
            zenpack install /opt/zenoss/packs/ZenPacks.zenoss.ApacheMonitor-2.1.3-py2.7.egg
            zopectl restart

    .. tip::

        If you're getting following error, then try restarting::

            $ zenpack install /opt/zenoss/packs/ZenPacks.zenoss.ApacheMonitor-2.1.3-py2.7.egg
            Error: Required daemon zeneventserver not running.
            Execute 'zeneventserver start' and retry the ZenPack installation.

            $ zeneventserver restart
            stopping...
            starting...
            Waiting for zeneventserver to start...........

            $ zenpack install /opt/zenoss/packs/ZenPacks.zenoss.ApacheMonitor-2.1.3-py2.7.egg

**Using plugin**
    First: `Read plugin documentation <http://community.zenoss.org/community/documentation/official_documentation/zenoss-extended-monitoringRead plugin documentation>`_.
    Usually the steps are like following:

    - Navigate: Infrastructure -> Devices -> Select server from the list
    - From the bottom: Icon (Gear) -> Bind template -> Add template from ``Available`` section into ``Selected``
    - Select Monitoring Templates -> <Template>
    - Click Data Sources to configure

**Monitoring log file**
    Zenoss itself prefers monitoring resources with SNMP and syslog, whereas Trac's capabilities for logging are
    limited. Fortunatelly, Zenoss can run and read Nagios_ plugins. For the purpose we'll use
    `check_logfiles <http://labs.consol.de/nagios/check_logfiles/>`_ plugin. Steps for installation:

    #.  Download and compile plugin::

            wget http://labs.consol.de/download/shinken-nagios-plugins/check_logfiles-3.5.1.tar.gz
            tar -xzf check_logfiles-3.5.1.tar.gz
            cd check_logfiles-3.5.1
            ./configure
            make

    #.  Copy built binary to Zenoss libexec directory::

            scp plugins-script/check_logfiles zenoss@monitor.setup.com:/opt/zenoss/libexec

    #.  Create configuration file for ``check_logfiles`` command (example)::

            # Example config file for check_logfiles Nagios plugin
            # Location: /etc/trac/check_logfiles.cfg
            @searches = (
            {
                tag => "mysql",
                logfile => "/var/log/mysql/error.log",
                criticalpatterns => "ERROR"
            },
            {
                tag => "multiproject",
                logfile => "/var/log/trac/multiproject.log",
                rotation => 'loglog0log1',
                criticalpatterns => "ERROR"
            });

        .. tip::

            `See plugin documentation <http://labs.consol.de/nagios/check_logfiles/>`_ for further information

    #.  Create ZenCommand for running Nagios plugin (see official documentation: http://community.zenoss.org/docs/DOC-2514)

        #.  Select Infrasturcture > Monitoring templates > Device (Server/Linux)
        #.  Add new Data source by clicking the plus icon:

            - Name: CheckLogfiles
            - Type: COMMAND

        #.  Doubleclick created datasource for editing and set:

            - Enabled: True
            - Use SSH: False
            - Parser: Nagios
            - Command template::

                /opt/zenoss/libexec/check_logfiles -f /etc/trac/check_logfiles.cfg

            - Component: CheckLogfiles
            - Event Key: Nagios

            You may want to test command by setting the hostname in field and clicking the Test

        #.  Save changes

    Now you set triggers to events coming from log files


.. _extra-varnish:

Varnish for HTTP caching
========================
Varnish is a web application accelerator that works as a HTTP proxy, taking most of the HTTP communication hit
for non-dynamic pages.

.. todo:: Write about Varnish



.. _install-extra-ldap:

LDAP: Authentication backend
============================
MultiProject comes with built-in LDAP authentication support, which can also be used next to other
authentication backends: when user logs into service, the


#.  Optional: Install LDAP server (or use existing LDAP server):

    - Install software::

        sudo apt-get install slapd

        Omit OpenLDAP server configuration? ... No
        DNS domain name: localhost
        Name of your organization: localhost
        Admin Password: XXXXX
        Confirm Password: XXXXX
        Database type: BDB
        Do you want your database to be removed when slapd is purged? ... No
        Move old database? ... Yes
        Allow LDAPv2 Protocol? ... No

      .. tip::

        In CentOS the server is installed a bit differently:

        #. Install software::

            yum install openldap-servers openldap-clients``

        #.  Modify configuration::

                # /etc/openldap/ldap.conf
                BASE    dc=setup,dc=company,dc=com
                URI     ldap://localhost:389/ ldapi://localhost:636/

                # /etc/sysconfig/ldap
                SLAPD_OPTIONS="-h ldap://127.0.0.1:389/"

        #.  Create password has with command::

                sudo slappasswd
                password:
                {SSHA}generatedhash

        #.  Update the values in ``/etc/openldap/slapd.d/cn\=config/olcDatabase\=\{1\}bdb.ldif`` (number may be different)
            by replacing::

                #olcRootDN: cn=Manager,dc=my-domain,dc=com
                olcRootDN: cn=admin,dc=company,dc=com
                # Create if needed
                olcRootPW: {SSHA}generatedhash

        See also `CentOS documentation <http://www.centos.org/docs/5/html/Deployment_Guide-en-US/s1-ldap-quickstart.html>`_

    - Set the address the service is listening by modifying the value in ``/etc/defaults/slapd``::

        SLAPD_SERVICES="ldap://localhost:389/ ldapi://localhost:636/"

    - Start service::

        sudo /etc/init.d/slapd start

    - Create ``base.ldif`` file with contents similar to following::

        # Create top-level object in domain
        dn: dc=company,dc=com
        objectClass: top
        objectClass: dcObject
        objectclass: organization
        o: Example Organization
        dc: company
        description: LDAP Example

        # Admin user.
        dn: cn=admin,dc=company,dc=com
        objectClass: simpleSecurityObject
        objectClass: organizationalRole
        cn: admin
        description: LDAP administrator
        userPassword: XXXXXX

        dn: ou=people,dc=company,dc=com
        objectClass: organizationalUnit
        ou: people

        dn: ou=groups,dc=company,dc=com
        objectClass: organizationalUnit
        ou: groups

    - Insert record into LDAP database::

        sudo ldapadd -x -D cn=admin,dc=company,dc=com -W -f base.ldif


    .. tip::

       You can also use external services like phpLDAPadmin_ to
       manage the LDAP server.

#.  Install python dependencies::

        sudo pip install python-ldap

#.  Configure LDAP connection in MultiProject config: ``project.ini``:

    Add LDAP authentication class ``multiproject.core.auth.ldap_auth.LdapAuthentication``
    into ``authentication_providers`` and ``ldap`` in ``authentication_order``

    .. code-block:: ini

        authentication_order = local,ldap
        authentication_providers = multiproject.core.auth.local_auth.LocalAuthentication,multiproject.core.auth.ldap_auth.LdapAuthentication

        # Connection url, user and password for LDAP server
        ldap_connect_path = ldap://localhost:389
        ldap_bind_user = cn=admin,dc=company,dc=com
        ldap_bind_password = *******
        # Parameter that identifies the user. Usually "uid" or "cn"
        ldap_uid = uid
        ldap_user_rdn = o=people,
        ldap_base_dn = dc=company,dc=com
        ldap_object_classes = inetOrgPerson
        ldap_use_tsl = False
        ldap_use_sasl = False

    .. note::

        Creating LDAP connections using TSL or SASL are not support atm.

#.  Optional: Put users coming from LDAP into organization. See :ref:`usage-org-update`

#.  Restart server::

        /etc/init.d/apache2 restart

.. _install-extra-gitosis:

Gitosis: SSH key authentication
===============================
Gitosis is a service to allow users to authenticate into git repositories with ssh public keys. MultiProject
supports this, but to integrate it into MultiProject and trac authentication system, it needs to be patched.

#.  Download the release and patch it::

        fab dist.build:ext=true

#.  Install package::

        tar -xzf dist/gitosis-0.2.tar.gz -C /tmp
        cd /tmp/gitosis-0.2/
        sudo python setup.py install


#.  Add git user into the system::

        sudo useradd --system -G apache --home-dir /var/www/trac/gitosis --shell /bin/bash git
        sudo mkdir -p /var/www/trac/gitosis /var/log/gitosis
        sudo chown -R git.git /var/www/trac/gitosis /var/log/gitosis

#.  Configure identity for git user::

        sudo -H -u git git config --global user.email "trac@localhost"
        sudo -H -u git git config --global user.name "Trac"

#.  Configure SSH server

    Ensure sshd configuration ``/etc/ssh/sshd_config`` that git user can log in. Suggested configuration values
    to set::

        PermitRootLogin no
        AllowUsers git
        PubkeyAuthentication yes
        RSAAuthentication yes
        PermitEmptyPasswords no
        PasswordAuthentication no

    .. TIP::

        On can also run Gitosis specific instance of SSH daemon. In this case, start service with custom configuration
        file::

            /usr/sbin/sshd -f /etc/trac/gitosis_sshd_config

#.  Configure Gitosis

    .. NOTE::

        To configure Gitosis, you do not edit files directly on the server.
        Instead, Gitosis provides a Git repository which contains the configuration.
        To update this configuration, you clone, commit, and push to ``gitosis-admin`` just as you would any other repository.

    #.  Create SSH keys for root (for administrating)::

            ssh-keygen -t rsa -b 2028 -f /root/.ssh/id_rsa

    #.  Initialize the gitosis repository::

            sudo -H -u git gitosis-init < /root/.ssh/id_rsa.pub
            sudo chmod +x /var/www/trac/gitosis/repositories/gitosis-admin/hooks/post-update

    #.  Clone the git admin repository::

            sudo su git
            git clone /var/www/trac/gitosis/repositories/gitosis-admin
            cd gitosis-admin

    #.  Edit the configuration (as git user)::

            vim gitosis.conf

        .. code-block:: ini

            [gitosis]
            repositories = /var/www/trac/repositories

            [group admins]
            members = <your user id>

            [group gitosis-admin]
            repositories = /var/www/trac/gitosis/repositories
            members = @admins

    #.  Commit and push the config (as git user)::

            git commit -a -m "Updated configuration"
            git push

#.  Set cron task to update keys from MultiProject UI in Gitosis, timely manner::

        sudo -u git crontab -e

        # Copy SSH public keys set via user settings to gitosis
        * * * * * python /var/www/trac/scripts/cron/gitosis_ssh_key_sync.py >> /var/log/gitosis/cron.log 2>&1

#.  Edit ``/etc/trac/project.ini`` to have following values:

    .. code-block:: ini

        [multiproject]
        gitosis_repo_path = /var/www/trac/gitosis/repositories/gitosis-admin
        gitosis_clone_path = /var/www/trac/gitosis/gitosis-clone
        gitosis_enable = True

#.  Try cloning the admin repository::

        git clone git@localhost:gitosis-admin.git

If the above works, then all projects should be clonable if their public key has been imported, and the user
in question has access to the project's version control. For more information on gitosis see
`Gitosis in ArchWiki <https://wiki.archlinux.org/index.php/Gitosis>`_.
