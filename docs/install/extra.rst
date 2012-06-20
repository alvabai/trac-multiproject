.. _install-extra:

==============
Extra features
==============
This chapter describes how to setup the optional/additional features to your MultiProject setup.
Install the components that you need.

.. contents::
   :local:

.. _install-extra-analytics:

Statistics: MultiProject analytics
==================================
MultiProject plugin comes with optional analytics service, where different kind of statistics can be
pulled from projects and it's usage. Follow the steps to enable it in your setup:

.. todo:: Write about MP analytics


#.  Create background tasks as cron jobs::

        sudo -u www-data crontab -e

    Contents::

        # Read event log from log to database (Frequently)
        0,6,12,18,24,30,36,42,48,54 * * * * python /storage/trac/dist/current/scripts/analytics/run_event_etl.py

        # Refresh summary data (Every hour)
        10 * * * * python /storage/trac/dist/current/scripts/analytics/summarize.py

        # Clone dimension data from operational database (Every day)
        0 4 * * * python /storage/trac/dist/current/scripts/analytics/dimension_sync.py


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

#.  Restart server::

        /etc/init.d/apache2 restart

.. _install-extra-gitosis:

Gitosis: SSH key authentication
===============================
Gitosis is a service to allow users to authenticate into git repositories with ssh public keys. MultiProject
supports this, but to integrate it into MultiProject and trac authentication system, it needs to be patched.

#.  Download the release and patch it::

        wget -O gitosis.tar.gz "http://eagain.net/gitweb/?p=gitosis.git;a=snapshot;h=dedb3dc63f413ed6eeba8082b7e93ad136b16d0d;sf=tgz"
        tar -xzf gitosis.tar.gz
        cd gitosis
        patch -p0 --ignore-whitespace < ../ext/patches/gitosis/*.patch
        sudo python setup.py install
        cd -


#.  Edit ``/etc/trac/project.ini`` to have following values:

    .. code-block:: ini

        gitosis_repo_path = /var/www/trac/gitosis/repositories/gitosis-admin
        gitosis_clone_path = /var/www/trac/gitosis/gitosis-clone
        gitosis_enable = True

#.  Configure SSH server

    Ensure sshd configuration ``/etc/ssh/sshd_config`` that git user can log in. Suggested configuration values
    to set::

        PermitRootLogin no
        AllowUsers git
        PubkeyAuthentication yes
        RSAAuthentication yes
        PermitEmptyPasswords no
        PasswordAuthentication no

#.  Add git user into the system::

        sudo adduser --system --disabled-password --ingroup www-data --home \
        /var/www/trac/gitosis --shell /bin/bash git

#.  Configure identity for git user::

        sudo -H -u git vim /var/www/trac/gitosis/.gitconfig

        [user]
        email = trac@localhost
        name = Trac

#.  Initialize the gitosis repository::

        sudo -H -u git gitosis-init < ~/.ssh/id_rsa.pub
        sudo chmod +x /var/www/trac/gitosis/repositories/gitosis-admin/hooks/post-update

#.  Clone the git admin repository::

        sudo chmod a+w .
        sudo -H -u git git clone /var/www/trac/gitosis/repositories/gitosis-admin
        cd gitosis-admin

#.  Edit the configuration::

        sudo -H -u git vim gitosis.conf

    .. code-block:: ini

        [gitosis]
        repositories = /var/www/trac/repositories

        [group admins]
        members = <your user id>

        [group gitosis-admin]
        repositories = /var/www/trac/gitosis/repositories
        members = @admins

#.  Commit and push the config::

        sudo -H -u git git commit -a -m "Fixed configuration."
        sudo -H -u git git push
        cd ..
        sudo rm -rf gitosis-admin

#.  Import your ssh key via MultiProject ui, then sync the keys::

        sudo -H -u git python /var/www/trac/dist/current/scripts/gitosis_ssh_key_sync.py

    Alternatively, update keys timely manner with cron job::

        sudo -u git crontab -e

        # Copy SSH public keys set via user settings to gitosis
        * * * * * source /etc/trac/env.sh; /var/www/trac/dist/current/scripts/gitosis_ssh_key_sync.py >> /var/www/trac/logs/git_cronlog 2>&1

#.  Try cloning the admin repository::

        git clone git@localhost:gitosis-admin.git

If the above works, then all projects should be clonable if their public key has been imported, and the user
in question has access to the project's version control. For more information on gitosis see
`Gitosis in ArchWiki <https://wiki.archlinux.org/index.php/Gitosis>`_.
