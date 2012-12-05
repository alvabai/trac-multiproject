# -*- coding: utf-8 -*-
"""
Module provides a simple announcement tool for admins.
Message is set in configuration::

    [multiproject-notifications]
    announce_text = This is the announcement in WikiSyntax.
        Notice how text can be multiline.

"""
import pkg_resources

from genshi.filters.transform import Transformer
from trac.config import Option
from trac.core import Component, implements
from trac.web import ITemplateStreamFilter
from trac.wiki import wiki_to_html
from trac.web.chrome import tag, ITemplateProvider, add_script

from multiproject.common.web.resource import IJSONDataPublisherInterface


class AnnounceBox(Component):
    implements(ITemplateStreamFilter, IJSONDataPublisherInterface, ITemplateProvider)

    announce_text = Option('multiproject-notifications', 'announce_text', default=None,
        doc='Wiki text to show for all the service users')
    announce_id = Option('multiproject-notifications', 'announce_id', default='multiproject-announce',
        doc='Unique identifier for announcement. When changed, the nofications is show to user again')

    # ITemplateStreamFilter methods

    def filter_stream(self, req, method, filename, stream, data):
        """
        Adds announcement box before the mainnav element
        """
        # Add element only if value is set
        if not self.announce_text:
            return stream

        add_script(req, 'multiproject/js/jquery.cookie.js')
        add_script(req, 'multiproject/js/announce.js')

        announcement = tag.div(
            tag.div(wiki_to_html(self.announce_text, self.env, req=req), class_='content'),
            tag.a(class_='close'),
            tag.div(class_='clear'),
            class_='announce'
        )

        # Add Syntax Highlight tab from user preferences
        trans = Transformer('.//div[@id="mainnav"]').before(announcement)
        return stream | trans

    # IJSONDataPublisherInterface

    def publish_json_data(self, req):
        return {'conf': {
            'announce_id': self.announce_id,
        }}

    # ITemplateProvider methods

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('multiproject.common.notifications', 'templates')]

    def get_htdocs_dirs(self):
        return [('multiproject', pkg_resources.resource_filename(__name__, 'htdocs'))]

