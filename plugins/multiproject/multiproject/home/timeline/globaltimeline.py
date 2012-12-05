from pkg_resources import resource_filename #@UnresolvedImport
import re

from trac.core import Component, implements, TracError
from trac.web.api import IRequestHandler, RequestDone
from trac.web.chrome import ITemplateProvider
from trac.web.chrome import Chrome, add_script
from genshi.input import HTML

from multiproject.home.timeline.api import GlobalTimeline
from multiproject.core.cache.timeline_cache import TimelineCache
from multiproject.core.configuration import conf

import math

class GlobalTimelineModule(Component):
    implements(IRequestHandler, ITemplateProvider)

    def __init__(self):
        self.cache = TimelineCache()

    # IRequestProvider
    def match_request(self, req):
        return re.match(r'/globaltimeline[.xml]?', req.path_info)

    def process_request(self, req):
        if req.path_info.endswith('.xml'):
            return self.show_rss_timeline(req)
        else:
            return self.show_html_timeline(req)

    # Methods for showing timeline in different formats
    def show_html_timeline(self, req):
        """
        Returns the HTML output
        """
        content = self.cache.get_global_timeline(req.authname)

        # Re-render content if not found in cache
        if not content:
            try:
                content = self.render_content_html(req)
                self.cache.set_global_timeline(req.authname, content)
            except Exception as e:
                self.log.exception('Failed to show timeline: %s' % e)
                raise TracError('Failed to show timeline')

        data = {'content': HTML(content)}

        return 'globaltimeline.html', data, None

    def show_rss_timeline(self, req):
        content = self.cache.get_global_timeline(req.authname, rss=True)

        # Re-render content if not found in cache
        if not content:
            try:
                content = self.render_rss(req)
            except Exception as e:
                self.log.exception('Failed to show timeline: %s' % e)
                return 'error.rss', {'msg':str(e)}, 'application/rss+xml'

        req.send(content, 'application/rss+xml')
        raise RequestDone


    # Methods for rendering timeline in different formats
    def render_content_html(self, req):
        """
        Renders the global timeline content in HTML format

        :param req: Trac request
        :raise: Exception in a case of rendering issues
        :return: Rendered HTML string
        """
        data = {'events':self._get_latest_events(req),
                'conf':conf,
                'math':math}
        chrome = Chrome(self.env)

        output = chrome.render_template(req, 'globaltimelinecontent.html', data, fragment=True)

        return output.render()

    def render_rss(self, req):
        """
        Renders the global timeline in RSS/XML format

        :param req: Trac request
        :raise: Exception in a case of rendering issues
        :return: Rendered RSS string
        """
        data = {'events':self._get_latest_events(req),
                'conf':conf}
        chrome = Chrome(self.env)

        output = chrome.render_template(req, "globaltimeline.rss", data, 'application/rss+xml')
        self.cache.set_global_timeline(req.authname, output, rss = True)

        return output

    # ITemplateProvider
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]

    def get_htdocs_dirs(self):
        return []

    def _get_latest_events(self, req):
        tl = GlobalTimeline()
        return tl.get_latest_events(req.authname, 150)
