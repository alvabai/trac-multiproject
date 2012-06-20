# -*- coding: utf-8 -*-
"""
Macro for wiki to include RSS feeds. Accesses any site that does not require
authentication and embeds the feed content to the wiki page.
"""
import re, urllib2

from xml.dom import minidom

from trac.core import Component, implements
from trac.wiki import IWikiMacroProvider
from trac.util.html import html

from multiproject.core.configuration import conf
from multiproject.core.cache.rss_cache import RssCache

class RSSMacros(Component):
    """
    The wiki module implements macro for RSS feeds. Cannot be used with
    feeds that require authentication.
    """
    implements(IWikiMacroProvider)

    def get_macros(self):
        """
        Return the names of all implemented macros from the component.
        """
        yield "ListRssFeed"

    def get_macro_description(self, name):
        """
        Returns a (multi line) plain (or wiki) text description of the macro.

        :param str name: Name of the macro to describe
        """
        if name == 'ListRssFeed':
            return ('List headers from given RSS feed. The feed must not require '
                    'authentication\n'
                    ' * give RSS URL as parameter\n'
                    ' * limit - limit items count\n'
                    ' * frame - select frame type (header|list|both)\n'
                    ' * title - add title header\n'
                    'Example:\n'
                    '{{{\n'
                    '[[ListRssFeed(http://some.host.com/rssfeed,frame=header,title=My RSS list,limit=10)]]\n'
                    '}}}')

    def expand_macro(self, formatter, name, content):
        """
        Executes the macro. When it is used as a Macro, and not as a wiki processor,
        the arguments to the macro are passed in content. If an error is caught
        in the macro, a small error title is printed.

        Example::

            <Cannot view RSS content: HTTP 404: Authorization denied.>

        :returns: RSS headers, in html formatting.
        """
        if name != 'ListRssFeed':
            return None
        if not content:
            return ''

        args = content.split(',')
        if not args:
            raise Exception("No argument.")

        try:
            return self.get_feed(self.get_settings(args))
        except Exception, e:
            self.log.exception("Rss Exception")
            return html.pre("<Cannot view RSS content: %s>" % str(e))

    def get_settings(self, args, hid='rssheader', cid='rsscontent', limit=50,
                     caption=''):
        """
        Parse settings from arguments given to the macro. Valid arguments are
        "frame", "title" and "limit". Valid format for the arguments is of sorts:

        Example::

            http://site.to.feed/rssfeed,frame=both,title=This is the title of the feeds,
            limit=10

        :param str args: Arguments to match.
        :returns: A tuple of settings (rss_link, header_id, content_id, limit)
        """
        attr_re = re.compile('(%s)=(.+)' % '|'.join([ 'frame', 'title', 'limit' ]))
        rss = ''
        while args:
            arg = args.pop(0).strip()
            match = attr_re.match(arg)
            if match:
                key, val = match.groups()
                if key == 'frame':
                    val = val.strip("\"\'")
                    if val == 'both' or val == 'header':
                        hid = 'rssframeheader'
                    if val == 'both' or val == 'list':
                        cid = 'rssframecontent'
                elif key == 'title':
                    caption = val
                elif key == 'limit':
                    limit = self.at_least_one(int(val), 50)
            else:
                if not rss:
                    rss = arg
        return rss, hid, cid, caption, limit

    def get_feed(self, settings):
        """
        Connects to the RSS feed, parses it through and returns html content which
        lists the found headers.

        .. TODO:: This should really use Genshi, since it renders content
        """
        items = []
        (rss, hid, cid, caption, limit) = settings
        rsscache = RssCache()
        headers = rsscache.get_rss_feed(rss)
        if not headers:
            headers = self.refresh_feed(rss, rsscache)
        for title, link, dateinfo, author in headers:
            if limit > 0:
                header = html.span(title) + html.div(dateinfo, id="rssupdated")
                if author:
                    header += html.div(" by {0}".format(author))
                header += html.a("Read more ..", href=link)
                items.append(html.div(header, id=hid))
                limit -= 1

        if caption:
            return html.h2(html.span(caption), class_="title", id="rss") + html.div(items, id=cid)
        else:
            return html.div(items, id=cid)

    def refresh_feed(self, rss, rsscache):
        """
        Parses through the content of rss feed, using a proxy, if configured,
        uses cache for the feed content if memcached is in use.
        """
        headers = []
        self.set_proxy(conf.http_proxy)
        xml = minidom.parse(urllib2.urlopen(rss))
        if xml:
            root = xml.documentElement
            for node in root.childNodes:
                if node.nodeName == "item":
                    headers.append(self.get_header(node))
                if node.nodeName == "channel":
                    for channel_child in node.childNodes:
                        if channel_child.nodeName == "item":
                            headers.append(self.get_header(channel_child))
            if len(headers) > 0:
                rsscache.set_rss_feed(rss, headers)
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

    def at_least_one(self, count, default):
        if count > 0:
            return count
        return default

    def set_proxy(self, proxy):
        if proxy:
            if proxy.lower().startswith("https:"):
                proxy = urllib2.ProxyHandler({'https' : proxy})
                urllib2.install_opener(urllib2.build_opener(proxy, urllib2.HTTPSHandler))
            else:
                proxy = urllib2.ProxyHandler({'http' : proxy})
                urllib2.install_opener(urllib2.build_opener(proxy, urllib2.HTTPHandler))
