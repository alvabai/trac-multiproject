# -*- coding: utf-8 -*-
"""
This module contains the fabric tasks for setting up **a new, dedicated environment** for the service.
See :mod:`tasks.dist` for packaging.
"""
__author__ = 'jumuston'

from fabric.api import prompt, task

from fablib.api import sudo, put, Service

@task
def create_users():
    """
    Creates system users and groups, required by service
    """
    sudo('addgroup devel')


@task
def install_requirements():
    """
    Installs software and services required by the software

    .. NOTE:: Requires interactions for setting MySQL and LDAP password
    """
    sudo("""
        apt-get -y update
        apt-get -y install apache2
        apt-get -y install mysql-server
        apt-get -y install git
        apt-get -y install subversion
        apt-get -y install python-memcache
        apt-get -y install python-ldap
        apt-get -y install python-sqlalchemy
        apt-get -y install libapache2-mod-python
        apt-get -y install libapache2-svn
        apt-get -y install python-mysqldb
        apt-get -y install python-svn
        apt-get -y install python-subversion
        apt-get -y install mercurial
        apt-get -y install unzip
        apt-get -y install slapd
        apt-get -y install ldap-utils
        apt-get -y install migrationtools
        apt-get -y install yui-compressor
        apt-get -y install python-setuptools
        apt-get -y install subversion
        apt-get -y install python-nose
    """)

    # Install apache modules
    sudo("""
        a2enmod dav
        a2enmod dav_fs
        a2enmod ssl"""
    )

@task
def reset_databases(dumpfile):
    """
    Recreate mysql database based from given dump
    """
    put(dumpfile, "dump.sql")

    mysql = Service('mysql')
    mysql.stop()

    sudo('rm -rf /var/lib/mysql/')
    sudo('mysql_install_db')

    mysql.start()

    # Set new password for tracuser
    password = prompt('Set password for database user "tracuser": ')

    sudo('mysqladmin -u root password "%s"' % password)

    sudo("""
    echo "UPDATE mysql.user SET password=password(\'\') WHERE user=\'tracuser\';" >> dump.sql
    echo "UPDATE mysql.user SET password=password(\'{0}\') WHERE user=\'root\';" >> dump.sql
    echo "UPDATE trac_admin.user SET sha1_pw=sha1(\'{0}\'), mail=\'root@localhost\';" >> dump.sql
    echo "flush privileges;" >> dump.sql
    mysql -u root --password={0} < dump.sql
    """.format(password))

    sudo('rm dump.sql')

