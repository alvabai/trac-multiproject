# -*- coding: utf-8 -*-
"""
The module generates RSS feeds for projects, based on request:

- /home/rss/newest.xml
- /home/rss/mostactive.xml
- /home/rss/featured.xml
- /home/rss/projects/<username>.xml

By default, the RSS feed is in RSS 2.0 format. By adding ``?format=rss10`` in the end
of the request, the service returns RSS 1.0 instead::

    /home/rss/projects/featured.xml?format=rss10

The validity of the RSS feed is done by: http://www.validome.org/rss-atom/validate

"""
from pkg_resources import resource_filename #@UnresolvedImport
import re

from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.web.chrome import ITemplateProvider

from multiproject.common.projects import Projects
from multiproject.core.configuration import conf

RSS_FEED_MODULE_REGEXP = re.compile(r'/rss/(?:newest|mostactive|featured|projects/.*).xml$')

class RSSFeedModule(Component):
    """
    Trac component for creating RSS feeds containing links and icons of
    most active, newest, or featured projects, or projects of a specified user.
    """
    implements(ITemplateProvider, IRequestHandler)

    # IRequestHandler methods
    def match_request(self, req):
        """ Path used for showing this page
        """
        return re.match(RSS_FEED_MODULE_REGEXP, req.path_info)

    def process_request(self, req):
        """ Process request for listing, creating and removing projects
        """
        prjs = Projects()
        data = {}
        store = conf.getUserStore()
        anon = store.getUser('anonymous')

        data['home'] = striptrail(conf.url_home_path) + "/rss"
        data['tracurl'] = striptrail(conf.url_home_path)

        # Having url_service here is probably a good idea. Otherwise RSS readers have no idea
        # where to fetch the relative path /project from.
        data['projroot'] = striptrail(conf.url_service)
        data['host'] = conf.domain_name
        data['url'] = striplead(striptrail(req.path_info))

        if re.match (r'/rss/mostactive.xml$', req.path_info):
            if anon:
                data['projects'] = prjs.get_projects_for_rss(anon.id, 0, 50, "MOSTACTIVE")
            data['title'] = 'Most active public projects'
        elif re.match (r'/rss/newest.xml$', req.path_info):
            if anon:
                data['projects'] = prjs.get_projects_for_rss(anon.id, 0, 50, "NEWESTFILTERED")
            data['title'] = 'Newest public projects'
        elif re.match (r'/rss/featured.xml$', req.path_info):
            if anon:
                data['projects'] = prjs.get_projects_for_rss(anon.id, 0, 50, "FEATURED")
            data['title'] = 'Featured projects'
        elif re.match(r'/rss/projects/.*.xml', req.path_info):
            username = req.path_info[req.path_info.rfind('/') + 1:-4]
            # username is validated in get_participated_public_projects
            data['projects'] = prjs.get_participated_public_projects(username)
            data['title'] = '%s\'s projects' % username
        else:
            data['projects'] = None

        # Support for both RSS 2.0 (default) and RSS 1.0 formats
        if 'rss10' == req.args.get('format', 'notset'):
            return "rss_feed_template.rss10", data, 'application/rss+xml'
        return "rss_feed_template.rss", data, 'application/rss+xml'

    # ITemplateProvider methods
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []

# Lambdas for stripping trailing and leading slashes
striptrail = lambda url: url[:-1] if url.endswith('/') else url
striplead = lambda url: url[1:] if url.startswith('/') else url
