# -*- coding: utf-8 -*-
from pkg_resources import resource_filename #@UnresolvedImport
from datetime import datetime
import re

from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf
from multiproject.core.users import get_userstore


class RSSServiceStatisticsModule(Component):
    """ Trac component for creating RSS feeds
    """
    implements(ITemplateProvider, IRequestHandler)

    # IRequestHandler methods
    def match_request(self, req):
        """ Path used for showing this page
        """
        # use this service only if it is configured
        if not conf.service_statistics:
            return False

        return re.match(r'/home/stats$', req.base_path + req.path_info)

    def process_request(self, req):
        """ Create a simple RSS feed based on this structure that shows the number of active projects and members.
            In the future we will add more details.
        """
        prjs = Projects()

        # create a list
        items = []

        # append tuples containing items to show
        items.append (('PROJECT_COUNT', 'Project count', prjs.project_count()))
        items.append (('ACTIVE_MEMBER_COUNT', 'Active member count', get_userstore().getMemberCountInProjects()))

        pubdate = datetime.now()

        data = {}
        data['items'] = items
        data['site'] = conf.url_statistics

        # pubDate format: Wed, 12 Jan 2011 11:47:29 GMT
        data['pubdate'] = pubdate.strftime("%a, %d %B %Y %H:%M:%S %Z")

        return "service_statistics.rss", data, 'application/rss+xml'

    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []
