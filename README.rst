========================
Multiproject Trac Plugin
========================
Multiproject is a Trac plugin, that allows multiple project hosting in Trac
environments. Multiproject features an administration project, which can be used to
define site front page, manage local and ldap groups and users, and a convenient
way of hosting multiple trac projects. For more information, check the project home
page, https://projects.developer.nokia.com/multiproject

Complete documentation can be found from ``docs/`` folder.


Configuration
=============
This section explains some of the most common and required configuration options to get your multiproject
plugin running, and perhaps tweaking it a little bit. Multiproject plugin offers templates for most required
configuration options, save for ``/etc/trac/env.sh``, but this documentation already offers an example for
this little environment definition. See: :ref:`environment-configuration`.

Configurations are in the version control, in sub dir ``etc/templates``. See: :ref:`repository-contents`.

The configuration files are template files, containing substitutable variables, in form ``${variable_name}``.
These variables are replaced with fabric tasks ``dist.buildetc`` or ``dist.build``. Using fabric to build
the plugin, these configuration files are included into the source code release packages, but building the
eggs manually, these variables need also to be replaced manually.

.. toctree::

    configuration

