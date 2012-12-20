.. highlight:: bash

.. _manual-installation:

.. _install-plugin:

=======
Plugins
=======
Just like Trac, also MultiProject powered setup can be extended with the plugins. This chapter lists the plugins
and installation instructions for the ones that are being successfully used/customized for MultiProject based Trac setup.

===================================  ==============================================================
Plugin                               Description
===================================  ==============================================================
:ref:`install-plugin-multiproject`   The plugin itself. Comes with many components to be enabled
                                     for home and projects
:ref:`install-plugin-batchmodify`    Modify several tickets at once
:ref:`install-plugin-downloads`      Project releases and downloads
:ref:`install-plugin-discussion`     Discussion forum
:ref:`install-plugin-mastertickets`  Related tickets
:ref:`install-plugin-childtickets`   Subtickets and tasks
:ref:`install-plugin-xmlrpc`         Provides XMLRPC_ interface for project resources
:ref:`install-plugin-customfield`    Manage custom fields via web ui
:ref:`install-plugin-git`            Version control backend support for GIT
:ref:`install-plugin-hg`             Version control backend support for Mercurial
:ref:`install-plugin-svn`            Version control backend support for SVN
===================================  ==============================================================


.. _install-plugin-multiproject:

MultiProject
------------

About configuration
    MultiProject plugin comes with few configuration template, found in the package (``etc/templates/trac/``):

    - ``project.ini``: Main configuration file, containing configuration keys and value for Trac environment and MultiProject
      plugin. All the projects inherits this file as well.
    - ``home.ini``: Home project has different set of plugins to be enabled.
    - ``multiproject.conf`` and ``multiproject-access.conf``: Ready made configuration files for Apache

    .. figure:: ../_static/config.png
       :align: center
       :scale: 70 %

       Configuration inheritance

Installation
    #.  MultiProject plugin is/should be installed already :ref:`with the dependencies <install-server-dep>`.

    #.  Copy and link configuration files from package::

            sudo cp etc/trac/* /var/www/trac/config/
            sudo ln -s /var/www/trac/config/ /etc/trac/

    #.  Set salt

        Salt is a random string of characters that is used for
        improves the security of the generated tokens and password storage

        - Generate unique string for example with ``pwgen`` command::

            pwgen --symbols --numerals -1 40 1

        - Set value in ``project.ini``:

          .. code-block:: ini

            [multiproject]
            salt = <put random string here>

    #.  Migrate database

        The so called ``empty_database.sql`` contains the initial version/structure of the required data storage, on top of
        which the data migrations are created. Thus, after restoring the database it needs to be migrated to latest version.
        Run update script found in the package::

            python scripts/update.py

            STATUS      MIGRATION
            ---------------------------------------------------------------
            installed : 20110906120000_authentication_method_datatype
            installed : 20111207083300_wiki_start_time_to_utimestamp
            installed : 20120209130000_user_created
            new       : 20120210150000_project_events


            To install migrations, run:
                python update.py --update-new
                    - Runs all new migration. Shorthand: -u

            Other options are:
                --update-to=MIGRATION, -t=MIGRATION
                    - Runs all migrations up or down to the given name
                --cherry-pick-update=MIGRATION, -p=MIGRATION
                    - Tries to update one, single migration. Dangerous!
                --cherry-pick-downgrade=MIGRATION, -d=MIGRATION
                    - Tries to downgrade one, single migration. Dangerous!


        In this case, the database would be upgraded with command::

            python update.py --update-new

    #.  Copy version control hooks from the package::

            sudo mkdir -p /var/www/trac/scripts
            sudo cp -r scripts/* /var/www/trac/scripts

        .. warning::

            If there are projects created prior to changing the version control hook location, it is necessary
            to go through all existing projects and fix the symlinks for the hooks.

        And as noted before this location can be configured via ``/var/www/trac/config/project.ini``

        .. code-block:: ini

            [multiproject]
            version_control_hooks_dir = /var/www/trac/scripts/hooks

    #.  Prepare cron jobs::

            sudo cp -a scripts/cron/* /var/www/trac/scripts

        Modify cron jobs if needed (``sudo crontab -u www-data -e``)::

            # Generate global timeline event data from project specific timeline events
            0 * * * * python /var/www/trac/scripts/rss_generator.py

            # Goes through projects to see how much resources they consumes
            #0 3 * * * /var/www/trac/scripts/cron/storageusage.sh

            # Send watchlist mail notification
            */5 * * * * python /var/www/trac/scripts/cron/watchlist_notify.py immediate
            0 0 * * * python /var/www/trac/scripts/cron/watchlist_notify.py daily
            30 0 * * 1 python /var/www/trac/scripts/cron/watchlist_notify.py weekly

            # Do indexing for projects. Needed for explore projects feature.
            0 6,18 * * * nice python /var/www/trac/scripts/cron/generate_project_user_visibility.py 2>&1 > /tmp/generate_project_user_visibility.log

.. _install-plugin-batchmodify:

BatchModify
-----------
Batch modify is a 3rd party plugin, which is optional for MultiProject setups. However, it does provide a handy
way to modify multiple tickets at once. In order to work with MultiProject, batchmodify requires slight modifications,
thus being currently forked and hosted in separate repository.

#.  Install plugin from project repository::

        git clone https://projects.developer.nokia.com/git/batchmodify.git
        cd batchmodify
        sudo python setup.py clean
        sudo python setup.py install
        cd -

#.  Enable the plugin by setting in  ``/etc/trac/project.ini``:

    .. code-block:: ini

        [components]
        batchmod.web_ui.batchmodifymodule = enabled

.. _install-plugin-discussion:

TracDiscussion
--------------
Trac Discussion is a plugin that provides a discussion forum for the project.
Plugin is currently required with the MultiProject setup. Also, the plugin is heavily modified to have fixes
and changes suitable for the MultiProject environment. And so a fork is hosted separately.

#.  Install plugin::

        git clone https://projects.developer.nokia.com/git/tracdiscussion.git
        cd tracdiscussion
        sudo python setup.py clean
        sudo python setup.py install
        cd -

#.  Configure plugin in ``/etc/trac/project.ini``:

    .. code-block:: ini

        [components]
        tracdiscussion.* = enabled

        [discussion]
        additional_options = use_default_forum
        forum_sort = subject
        messages_per_page = 20
        topics_per_page = 20

#.  Optional: you may want to disable the plugin for home project by setting the
    value in ``/var/www/trac/projects/home/conf/trac.ini``:

    .. code-block:: ini

        [components]
        tracdiscussion.* = disabled

.. _install-plugin-downloads:

TracDownloads
-------------
TracDownloads is a plugin that provides a discussion forum for the project.
This plugin has also gone through some changes and security fixes to suite better into the
needs of MultiProject, so a fork is hosted separately.

.. note::

    Currently, the TracDownloads functionality is replaced with the
    Files Downloads feature (see :ref:`import-old-files`), and you
    should disable the TracDownloads plugin or not install it at all.

#.  Install plugin::

        git clone https://projects.developer.nokia.com/git/tracdownloads.git
        cd tracdownloads
        sudo python setup.py clean
        sudo python setup.py install
        cd -

#.  Enable and configure plugin in ``/etc/trac/project.ini``:

    .. code-block:: ini

        [components]
        tracdownloads.* = enabled
        tracdownloads.core.downloadsdownloads = disabled

        [downloads]
        download_sort = file
        download_sort_direction = asc
        ext = all
        platform_sort = id
        platform_sort_direction = asc
        type_sort = id
        type_sort_direction = asc

#.  Optional: disable plugin in home project (``/var/www/trac/projects/home/conf/trac.ini``):

    .. code-block:: ini

        [components]
        tracdownloads.* = disabled

.. _install-plugin-mastertickets:

MasterTickets
-------------
Trac mastertickets is a plugin that allows users to make tickets block other tickets. It also allows
drawing of dependencies between tickets, if graphviz has been installed. Together with childtickets,
it offers quite good possibility of doing dependant tickets. MultiProject plugin uses the master version:

#.  Install plugin (directory name depends on current revision)::

        wget --no-check-certificate -O trac-mastertickets.tar.gz https://github.com/coderanger/trac-mastertickets/tarball/master
        tar -xzf trac-mastertickets.tar.gz
        cd coderanger-trac-mastertickets-43a7537
        sudo python setup.py install
        cd -

#. Install graphviz if not installed already::

        sudo apt-get install graphviz

#.  Configure plugin and set custom fields in ``/etc/trac/project.ini``:

    .. code-block:: ini

        [components]
        mastertickets.* = enabled

        [ticket-custom]
        blockedby = text
        blockedby.label = Blocked By
        blocking = text
        blocking.label = Blocking

#.  MasterTickets will also create graphviz compatible graphs about tickets, if graphviz package is installed.
    The dot command location can be customized:

    .. code-block:: ini

        [mastertickets]
        dot_path = /opt/local/bin/dot

#.  Additionally, if the graphviz is installed, enabling following components will allow looking at ticket
    dependencies:

    .. code-block:: ini

        [components]
        graphviz.graphviz.graphviz = enabled

#.  You may wanto to disable feature in home project ``/var/www/trac/projects/home/conf/trac.ini``:

    .. code-block:: ini

        [components]
        mastertickets.* = disabled
        childtickets.* = disabled

    This is because home projects don't have ticket system to begin with. In theory they could have, but home project
    is meant to be the "front page" or administrative project for the whole site. For more information on mastertickets
    see `MasterTicketsPlugin <http://trac-hacks.org/wiki/MasterTicketsPlugin>`_.

.. important::

    If mastertickets plugin is enabled *after* the projects are created been created,
    these project environments needs to be upgraded with command::

        sudo trac-admin /var/www/trac/projects/<project> upgrade

.. _install-plugin-childtickets:

Childtickets
------------
Childtickets plugin makes it possible to create subtickets to the tickets.
Plugin is modified for MultiProject, thus being hosted as a fork in separate repository.

#.  Install plugin::

        git clone https://projects.developer.nokia.com/git/childtickets.git
        cd childtickets
        sudo python setup.py clean
        sudo python setup.py install
        cd -

#.  Enable plugin and set custom fields in ``/etc/trac/project.ini``:

    .. code-block:: ini

        [components]
        childtickets.* = enabled

        [ticket-custom]
        parent = text
        parent.format = wiki
        parent.label = Parent ID

.. _install-plugin-customfield:

CustomFieldAdmin
----------------
Trac CustomFieldAdmin allows project admins to manipulate what custom fields are shown in tickets. The

#.  Latest Trac 0.11 version is compatible with Trac 0.12, so installing this is to just drop in the egg::

        svn co http://trac-hacks.org/svn/customfieldadminplugin/0.11 -r 11265 trac-customfieldadmin
        cd trac-customfieldadmin
        sudo python setup.py install
        cd -

#.  Enable plugin in ``/etc/trac/project.ini``:

    .. code-block:: ini

        [components]
        customfieldadmin.* = enabled

#.  Optional: disable the plugin in home project (``/var/www/trac/projects/home/conf/trac.ini``):

    .. code-block:: ini

        [components]
        customfieldadmin.* = disabled

.. important::

    It is important to know, that the plugin manipulates project's ``[ticket-custom]`` section. So, if
    Trac MasterTickets or Trac Childtickets is in use, ensure that ``[ticket-custom]`` is present in
    ``/etc/trac/project.ini`` and holds the values that these plugins require. Otherwise, project admins might
    be able to make their project unusable by removing these items. If they're present in the global configuration,
    the items upon removal will reappear in the admin ui. Downside to this is, that the admin plugin will print
    a warning about unsorted items.

.. _install-plugin-xmlrpc:

TracXMLRPC
-----------
Trac XMLRPC plugin allows controlling the trac remotely via various tools, or rather via a specific interface.
MultiProject depends on a specific version due to somewhat customized api::

    svn co http://trac-hacks.org/svn/xmlrpcplugin/trunk -r 8869 trac-xmlrpc
    cd trac-xmlrpc
    sudo python setup.py install
    cd -

TracWysiwyg
-----------
Trac Wysiwyg plugin makes it possible for editing content in visual mode.

#.  Install plugin::

        sudo pip install http://trac-hacks.org/svn/tracwysiwygplugin/0.12

#.  Enable plugin in ``project.ini``::

        [components]
        tracwysiwyg.* = enabled


.. _install-plugin-svn:

Subversion
----------
Subversion support comes built-in with the Trac. All you need is the python bindings to subversion, which is usually
shipped with the subversion. To test the bindings, run (no errors should be shown)::

    python
    >>> import svn
    >>>

.. _mercurial-installation:

.. _install-plugin-mercurial:

.. _install-plugin-hg:

TracMercurial
-------------
TracMercurial_ plugin provides the Mercurial version control support for Trac_.
Plugin is `compatible only with selected Mercurial versions <http://trac.edgewall.org/wiki/TracMercurial#Releases>`_.
Project page contains a compatibility table, whereas following combinations are tested:

============  ==============  =============
Mercurial     TracMercurial   Compatibility
============  ==============  =============
1.7.5         0.12.0.29       OK
1.8           0.12.0.29       OK
1.9           0.12.0.29       NOT OK
2.0           0.12.0.29       NOT OK
============  ==============  =============

#.  Install Mercurial (both methods supported, just ensure the version compatibility)::

        # Using system package manager
        sudo apt-get install mercurial

        # Using python installer (requires python headers)
        sudo pip install mercurial==1.9

#.  Install TracMercurial plugin::

        hg clone https://hg.edgewall.org/trac/mercurial-plugin
        cd mercurial-plugin
        hg up 0.12
        sudo python setup.py install

#.  Instal hgweb CGI script from MultiProject_ repository::

        sudo cp -a ext/libs/hgweb /var/www/trac/
        sudo chown -R www-data.www-data /var/www/trac/hgweb

#.  Update Apache configuration (``/var/www/trac/config/multiproject.conf``)::

        ScriptAlias /hg/ /var/www/trac/hgweb/hgwebdir.cgi/

#.  Configure the hgweb script by editing ``/var/www/trac/hgweb/hgweb.config``:

    .. code-block:: ini

        [web]
        baseurl = /hg
        push_ssl=false
        allow_push = *
        style = gitweb
        allow_archive = bz2 gz zip

        [collections]
        /var/www/trac/repositories = /var/www/trac/repositories

#.  Disable all TracMercurial sub-components in shared project configuration file ``/etc/trac/project.ini``,
    but leave options:

    .. code-block:: ini

        [components]
        tracext.hg.* = disabled

        [hg]
        node_format = short
        show_rev = yes

#.  Enable only the plugin accessor in home project configuration (``/etc/trac/home.ini``),
    so a new project with Mercurial can be created:

    .. code-block:: ini

        [components]
        tracext.hg.backend.mercurialconnector = enabled

Now, if project creation with Mercurial and hg clone for the project does work, the configuration was successful.

.. tip::

    If you are experiencing problems with Mercurial, :ref:`check the version compatibility table <install-plugin-hg>`.

.. _install-plugin-git:

TracGit
-------
TracGit_ plugin offers a Trac integration to Git_ version control system. Plugin gives Git
repository views into Trac's source browser, integrates it into timeline and adds a content parser for Git hash
refs to point into specific commits. Trac Git plugin offers a front end and some customization to Source code browser in Trac.
MultiProject uses the latest version of the TracGit plugin, at least for the time being.

.. note::

    TracGit_ supports Git version starting from 1.5.6, but some features like repository archive requires
    more up-to-date version. Using Git 1.7.10 or better is suggested.


#.  Install Git_ using system's package manager::

        sudo apt-get install git

#.  Configure ``git-core`` path in Apache configuration ``/etc/apache2/conf.d/multiproject.conf`` to match with the
    Git installation:

    .. code-block:: apacheconf

        ScriptAliasMatch "^/git(/.+?)(\.git)?/(.*)?" /usr/lib/git-core/git-http-backend/$1/$3

    .. note::

        At least in CentOS_ the path is ``/usr/libexec/git-core`` instead of ``/usr/lib/git-core``

#.  Install TracGit plugin::

        git clone https://github.com/hvr/trac-git-plugin
        cd trac-git-plugin
        sudo python setup.py install
        cd -

#.  Enable Git project creation in home project (``/etc/trac/home.ini``):

    .. code-block:: ini

        [components]
        tracext.git.git_fs.gitconnector = enabled

#.  Enable Git backend in global configuration in ``/etc/trac/project.ini``:

    .. code-block:: ini

        [git]
        cached_repository = false
        git_bin = /usr/bin/git
        persistent_cache = false
        shortrev_len = 7
        use_committer_id = true

How it works
    When the project with Git repository is created from web ui, it automatically enables the plugin in the specified project
    config:

    .. code-block:: ini

        [components]
        tracext.git.* = enabled

        [trac]
        repository_type = git

.. note::

    For more information on Trac Git plugin, see `GitPlugin project page <http://trac-hacks.org/wiki/GitPlugin>`_.
    The source is hosted in `Github <https://github.com/hvr/trac-git-plugin>`_.
