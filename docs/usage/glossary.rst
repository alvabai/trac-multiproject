========
Glossary
========
This chapter contains descriptions for the main configuration keys, environment variables and glossaries.

.. contents::
   :local:

Terminologies
=============
Terms and glossaries used by the software.

..  glossary::

    Trac
        Trac_ is an enhanced wiki and issue tracking system for software development projects, developed by Edgewall.
        Software is open source licensed.

Environment variables
=====================
The most relevant environment variables used by the software

..  envvar:: ROOT

    Points to root directory of the Multiproject setup. Usually defined in ``/etc/trac/env.sh``,
    having a value ``/var/www``.

..  envvar:: HOME

    Points to user's home directory. Usually system users do not have home directory, but with Multiproject
    the Apache needs to have one. See :ref:`install-apache`.

..  envvar:: FL_CONF_PATH

    Alternative way to provide used Funkload configuration file.
    See: :ref:`develop-test`