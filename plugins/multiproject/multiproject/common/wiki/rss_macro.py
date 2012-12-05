# -*- coding: utf-8 -*-
"""
Macro for wiki to include RSS feeds. Accesses any site that does not require
authentication and embeds the feed content to the wiki page.
"""
import re, urllib2
import datetime
from urlparse import urlparse
from xml.dom import minidom
from pkg_resources import resource_filename

from genshi.core import Attrs
from genshi.filters import Transformer
from genshi.filters.transform import ENTER

from trac.config import Option
from trac.core import Component, implements
from trac.web import ITemplateStreamFilter
from trac.web.chrome import ITemplateProvider, Chrome
from trac.wiki import IWikiMacroProvider
from trac.util.html import html
from trac.util.datefmt import utc

from multiproject.core.db import safe_int
from multiproject.core.cache.rss_cache import RssCache


class RSSMacros(Component):
    """
    The wiki module implements macro for RSS feeds. Cannot be used with
    feeds that require authentication.
    """
    implements(IWikiMacroProvider, ITemplateProvider)
    http_proxy = Option(
        section='multiproject', name='http_proxy',
        doc='HTTP proxy to be used when connecting to external resources. Example: http://myproxy:8080/'
    )

    def get_macros(self):
        """
        Return the names of all implemented macros from the component.
        """
        yield "ListRssFeed"

    def get_macro_description(self, name):
        """
        Return a (multi line) plain (or wiki) text description of the macro.

        :param name: Name of the macro to describe
        """
        if name == 'ListRssFeed':
            return ('List headers from given RSS feed. The feed must not require '
                    'authentication\n'
                    ' * give RSS URL as parameter\n'
                    ' * limit - limit items count. Default is 10.\n'
                    ' * title - add title header\n'
                    ' * separator - show separator (true|false). Default is true.\n'
                    ' * icon - show rss icon (true|false). Default is true.\n'
                    ' * full_link - URL for full post list. Default is empty.\n'
                    'Example:\n'
                    '{{{\n'
                    '[[ListRssFeed(http://some.host.com/rssfeed,title=My RSS list,limit=10,\n'
                    'separator=false,icon=true,full_link=http://some.host.com)]]\n'
                    '}}}')

    def expand_macro(self, formatter, name, content):
        """
        Execute the macro. When it is used as a Macro, and not as a wiki processor,
        the arguments to the macro are passed in content. If there is an error
        getting the RSS content, a brief error text is printed.

        :returns: RSS headers, in html formatting.
        """
        if name != 'ListRssFeed':
            return None
        if not content:
            return ''

        args = content.split(',')
        if not args:
            raise Exception("No argument.")

        req = formatter.req
        data = {}
        (data['rss'], data['caption'], data['limit'],
         data['separator'], data['icon'], data['full_link']) = self.get_settings(args)
        try:
            data['items'] = self.get_feed(data['rss'], data['limit'])
        except Exception, e:
            self.log.exception("Settings Exception")
            return html.pre("<Cannot view RSS content: %s>" % str(e))

        return Chrome(self.env).render_template(req, 'list_rss_feed.html', data, fragment=True)

    def get_settings(self, args, limit=10, caption='', separator='true', icon='true', full_link=''):
        """
        Parse settings from arguments given to the macro. Valid arguments are
        "title", "limit", "separator", "icon", and "full_link".
        Valid format for the arguments is of sorts:

        Example::

            http://site.to.feed/rssfeed,title=This is the title of the feeds,
            limit=10,separator=false,icon=true,full_link=http://some.host.com

        :param args: Arguments to match.
        :returns: A tuple of settings (rss_link, limit, separator, icon, full_link)
        """
        attr_re = re.compile('(%s)=(.+)' % '|'.join([ 'title', 'limit',
                                                      'separator', 'icon', 'full_link' ]))
        rss = ''
        while args:
            arg = args.pop(0).strip()
            match = attr_re.match(arg)
            if match:
                key, val = match.groups()
                if key == 'title':
                    caption = val
                elif key == 'limit':
                    limit = int(val) or 10
                elif key == 'separator':
                    if val == 'true' or val == 'True':
                        separator = 'rss_separator'
                    else:
                        separator = 'no_rss_separator'
                elif key == 'icon':
                    icon = val
                elif key == 'full_link':
                    full_link = val
            else:
                if not rss:
                    rss = arg
        return rss, caption, limit, separator, icon, full_link

    def get_feed(self, rss, limit=10):
        """
        Connect to the RSS feed. Parse it through and return a list of headers.
        Time zone of the datetime string is assumed to be UTC.

        :param rss: RSS feed URL
        :param limit: max number of wanted headers
        :returns: list of RSS header dicts
        """
        items = []
        limit = safe_int(limit)

        # Check and update cache
        rsscache = RssCache()
        headers = rsscache.get_rss_feed(rss)
        if not headers:
            headers = self.refresh_feed(rss)
            if headers:
                rsscache.set_rss_feed(rss, headers)

        for title, link, dateinfo, author in headers[:limit]:
            item = {
                'title': title,
                'link': link
            }

            try:
                # Parse date formats like: Mon, 24 Sep 2012 07:51:04
                item['dateinfo'] = datetime.datetime.strptime(dateinfo[0:-6], "%a, %d %b %Y %H:%M:%S")
            except ValueError:
                # Parse ISO format like: 2012-10-31T22:36:57
                item['dateinfo'] = datetime.datetime.strptime(dateinfo[0:-6], "%Y-%m-%dT%H:%M:%S")
            finally:
                item['dateinfo'] = item['dateinfo'].replace(tzinfo=utc)

            item['author'] = author
            items.append(item)

        return items

    def refresh_feed(self, rssurl):
        """
        Parses through the content of rss feed, using a proxy, if configured,
        uses cache for the feed content if memcached is in use.

        :param str rssurl: URL to RSS Feed
        :returns: List of RSS entries
        """
        headers = []

        opener = urllib2.build_opener()
        proxy = self.http_proxy

        # If proxy set, add custom handlers
        if proxy:
            urlinfo = urlparse(proxy)
            proxyhandler = urllib2.ProxyHandler({urlinfo.scheme : proxy})
            opener = urllib2.build_opener(proxyhandler, urllib2.HTTPHandler, urllib2.HTTPSHandler)

        # TODO: Use feedparser
        xml = minidom.parse(opener.open(rssurl))
        if xml:
            root = xml.documentElement
            for node in root.childNodes:
                if node.nodeName == "item":
                    headers.append(self.get_header(node))
                if node.nodeName == "channel":
                    for channel_child in node.childNodes:
                        if channel_child.nodeName == "item":
                            headers.append(self.get_header(channel_child))

        return headers

    def get_node_value(self, itemNode, node):
        """
        Read a value for text node. If the content is not text, empty string is
        returned.
        """
        for text_node in itemNode.childNodes:
            if text_node.nodeType == node.TEXT_NODE:
                return text_node.nodeValue
        return ""

    def get_header(self, node='', title='', link='', dateinfo='', author=''):
        for itemNode in node.childNodes:
            if itemNode.nodeName == "title":
                title = self.get_node_value(itemNode, node)
            elif itemNode.nodeName == "link":
                link = self.get_node_value(itemNode, node)
            elif itemNode.nodeName == "dc:date" or itemNode.nodeName == "pubDate":
                dateinfo = self.get_node_value(itemNode, node)
            elif itemNode.nodeName == "dc:creator" or itemNode.nodeName == "author":
                author = self.get_node_value(itemNode, node)
        return [title, link, dateinfo, author]

    def get_htdocs_dirs(self):
        """
        Return a list of directories with static resources (such as style
        sheets, images, etc.)
        """
        return []

    def get_templates_dirs(self):
        return [resource_filename('multiproject.common.wiki', 'templates')]


class RSSBasicAuth(Component):
    """
    Provides basic authentication by adding ``auth=basic`` to RSS feeds.
    Requires ``multiproject.common.users.login.BasicAuthRequest`` to be enabled
    """
    implements(ITemplateStreamFilter)

    # ITemplateStreamFilter methods

    def filter_stream(self, req, method, filename, stream, data):
        # If required component is disabled, skip this too
        if not self.env.is_component_enabled('multiproject.common.users.login.BasicAuthRequest'):
            return stream

        # Append auth=basic to href
        basic_auth = lambda stream: self._append_href(stream, {'auth': 'basic'})
        trans = Transformer('//a[@class="rss"]').apply(basic_auth)

        return stream | trans

    def _append_href(self, stream, params):
        """
        Append arguments to href

        :param Stream stream: Genshi stream
        :param dict params: Arguments to add
        :return:
        """
        for mark, (kind, data, pos) in stream:
            if mark is ENTER:
                attr_href = None
                try:
                    attr_href = [part for part in data if isinstance(part, Attrs) and part.get('href')][0]
                except KeyError:
                    self.log.warning('Found more/less than one href attributes - skipping')
                    yield mark, (kind, data, pos)

                # Add params into arguments
                # NOTE: Not using Href because ticket queries can be tricky
                parsed_href = urlparse(attr_href.get('href'))
                params_str = '='.join(['%s=%s' % (name, val) for name, val in params.items()])
                href = '%s?%s' % (parsed_href.path, params_str)
                if parsed_href.query:
                    href = '%s?%s&%s' % (parsed_href.path, parsed_href.query, params_str)

                # Replace href value in data
                attrs = data[1] | [('href', href)]
                data = (data[0], attrs)

            yield mark, (kind, data, pos)