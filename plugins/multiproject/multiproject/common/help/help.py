# -*- coding: utf-8 -*-
from trac.core import implements
from trac.web.api import ITemplateStreamFilter
from trac.web.href import Href
from trac.wiki.web_ui import WikiModule
from trac.util.translation import _
from genshi.builder import tag
from genshi.filters.transform import Transformer

from multiproject.core.configuration import Configuration
conf = Configuration.instance()


def use_home_url(name, event):
    href = event[1][1].get(name)
    base = conf.url_projects_path or '/'
    # Check where to split, because uri could be "/home" or "/trac/home"
    c = conf.url_home_path.count("/")
    # Reconstruct url pointing to project wiki to point into home wiki
    return '/'.join([conf.url_home_path] + href[len(base):].split('/', c + 1)[c:])


class HelpModule(WikiModule):
    """ Component for changing Help/Guide link and add Help tab on home
    """
    implements(ITemplateStreamFilter)

    def __init__(self):
        WikiModule.__init__(self, self.compmgr)

    def get_navigation_items(self, req):
        home = Href(conf.url_home_path)
        if 'WIKI_VIEW' in req.perm('wiki'):
            # Show Wiki on project Help on home
            if conf.resolveProjectName(self.env) != 'home':
                yield ('mainnav', 'wiki',
                    tag.a(_('Wiki'), href = req.href.wiki(), accesskey = 1))
            else:
                yield ('mainnav', 'wiki',
                    tag.a('Help', href = req.href.wiki()))
            # Change metanav to direct home wiki
            yield ('metanav', 'help',
                   tag.a(_('Help'), href = home('wiki'),
                         accesskey = 6))

    def filter_stream(self, req, method, filename, stream, formdata):
        """ Change all id="help" links to point home
        """
        transformation = ""
        try:
            transformation = stream | Transformer('//div[@id="help"]//a').attr('href', use_home_url)
        except:
            pass
        finally:
            return transformation
