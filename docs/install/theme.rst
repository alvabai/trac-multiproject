.. _install-theme:

=====
Theme
=====
MultiProject comes with a theme ``default``, that is designed for taking advantage from MultiProject -plugin.
The suggested method is to customize the built-in theme.


#.  Copy and link the theme folder::

        cp -r default /var/www/trac/themes/
        ln -s /var/www/trac/themes/default /var/www/trac/themes/current

#.  Define ``templates`` folder inside the theme directory in ``project.ini``::

        [inherit]
        templates_dir = /var/www/trac/themes/current/templates

    .. tip::

        By default, Trac serves the stylesheet, javascript and image resources by itself.
        This is inefficient, thus :ref:`use Apache to serve static files <install-extra-apache-static>`

#.  Empty Trac stylesheets (only needed with ``default`` theme)::

        cd /usr/lib/python2.6/site-packages/trac/htdocs/css
        sudo mv trac.css trac.disabled.css
        sudo mv report.css report.disabled.css
        sudo mv browser.css browser.disabled.css
        sudo mv ticket.css ticket.disabled.css
        sudo touch trac.css browser.css ticket.css report.css

#.  Define required aliases in Apache configuration:

    .. code-block:: apacheconf

        Alias /images       /var/www/trac/themes/current/htdocs/images
        Alias /htdocs/theme /var/www/trac/themes/current

        <Directory /var/www/trac/themes/current>
            ExpiresActive On
            ExpiresByType image/* "access plus 1 week"
            ExpiresByType text/css "access plus 1 week"
            ExpiresByType text/js "access plus 1 week"
            FileETag INode MTime Size
            Options -Indexes
            Order allow,deny
            Allow from all
        </Directory>

    .. note::

       These aliases are used by the ``default`` theme, delivered with the MultiProject plugin.





