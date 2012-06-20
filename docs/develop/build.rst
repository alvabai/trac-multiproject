
.. _develop-build:

========
Building
========
This chapter describes how to build MultiProject and its related tools.

.. highlight:: bash

.. contents::
   :local:

Building MultiProject
=====================
Fabric_ is being used for automate both local and remote tasks. Thus, it is also used for building
MultiProject package. In short, MultiProject package is built with command::

    fab dist.build:ext=true,compress=true,version="a.b.c"

To see all options and complete documentation for the task, run::

    fab -d dist.build

Release
-------
TBD


Configuration
-------------
This section explains some of the most common and required configuration options to get your MultiProject
plugin running, and perhaps tweaking it a little bit. MultiProject plugin offers templates for most required
configuration options, save for ``/etc/trac/env.sh``, but this documentation already offers an example for
this little environment definition. See: :ref:`install`.

Configurations are in the version control, in sub dir ``etc/templates``. See: :ref:`repository-contents`.

The configuration files are template files, containing substitutable variables, in form ``${variable_name}``.
These variables are replaced with fabric tasks ``dist.buildetc`` or ``dist.build``. Using fabric to build
the plugin, these configuration files are included into the source code release packages, but building the
eggs manually, these variables need also to be replaced manually.

There is also a specific fabric command to generate the configurations for each setup::

    fab dist.buildetc

The results will be build into ``build/etc/<setup>`` subdirectories.


Building environment tools
==========================
Sometimes (missing from repository, wrong version, compatibility issues...) there is a requirement to build some of the
used applications from sources. This sections contains some instructions how to do that.

.. tip::

    Running RedHat/CentOS? There is a `EPEL (Extra Packages for Enterprise Linux) <http://fedoraproject.org/wiki/EPEL>`_
    repository for you.


Building python and mod_python
------------------------------
With these instructions you can build python and mod_python Apache module from selected version.

#.  Install development tools::

        sudo apt-get install build-essential zlib1g zlib1g-dev \
        apache2-threaded-dev flex curl

#.  Build python::

        mkdir ~/tmp
        cd ~/tmp
        wget http://www.python.org/ftp/python/2.6.7/Python-2.6.7.tgz
        tar -zxf Python-2.6.7.tgz
        cd Python-2.6.7
        make distclean
        export LDFLAGS="-L/usr/lib/$(dpkg-architecture -qDEB_HOST_MULTIARCH)"
        ./configure --prefix=/opt/python-2.6.7

        make
        sudo make install
        sudo ln -s /opt/python-2.6.7 /opt/python
        unset LDFLAGS


#.  Build mod_python::

        cd ~/tmp
        svn co https://svn.apache.org/repos/asf/quetzalcoatl/mod_python/trunk/ mod_python-trunk
        cd mod_python-trunk

        # Put '-lm' in LDLIBS (http://code.google.com/p/modwsgi/issues/detail?id=115)
        vim configure
        #LDLIBS="${LDLIBS1} ${LDLIBS2}"
        LDLIBS="${LDLIBS1} -lm ${LDLIBS2}"

        ./configure --with-apxs=/usr/bin/apxs2 --with-python=/opt/python/bin/python
        make
        sudo make install

        # Put following PYTHONHOME line in /etc/apache2/envars
        export PYTHONHOME=/opt/python-2.6.7

        # Restart apache
        sudo /etc/init.d/apache2 restart


