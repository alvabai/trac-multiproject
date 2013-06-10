# -*- coding: utf-8 -*-
from trac.core import Component, implements
from trac.web import IRequestHandler
from trac.web.api import IRequestFilter
from trac.web.chrome import add_ctxtnav, INavigationContributor
from trac.versioncontrol.web_ui.changeset import AnyDiffModule
from trac.util.translation import _

from genshi.builder import tag
from genshi import HTML
from multiproject.core.users import get_userstore

from tracext.git.git_fs import GitRepository


class SourceViewContextNavFilter(Component):
    """
    Modifies following views for theme (and other purposes):

    - /browser
    - /diff
    - /log
    - /changeset (diff)
    - /changeset (single)
    """
    implements(IRequestFilter)

    def add_prevnext(self, req, elm_or_label, href=None, title=None):
        """Add an entry to the current page."""
        if href:
            elm = tag.a(elm_or_label, href=href, title=title)
        else:
            elm = elm_or_label
        req.chrome.setdefault('prevnext', []).append(elm)

    def prevnext_nav(self, req, prev_label, next_label, up_label=None):
        links = req.chrome['links']
        prev_link = next_link = None

        if not any(lnk in links for lnk in ('prev', 'up', 'next')): # Short circuit
            return

        if 'prev' in links:
            prev = links['prev'][0]
            prev_link = tag.a(prev_label, href=prev['href'], title=prev['title'],
                              class_='prev')

        self.add_prevnext(req, tag.span('', prev_link or prev_label,
                                        class_=not prev_link and 'missing' or None))

        if up_label and 'up' in links:
            up = links['up'][0]
            self.add_prevnext(req, tag.a(up_label, href=up['href'], title=up['title']))

        if 'next' in links:
            next_ = links['next'][0]
            next_link = tag.a(next_label, href=next_['href'], title=next_['title'],
                              class_='next')

        self.add_prevnext(req, tag.span(next_link or next_label, '',
                                        class_=not next_link and 'missing' or None))

    def prevnext_ctxnav(self, req, prev_label, next_label, up_label=None):
        links = req.chrome['links']
        prev_link = next_link = None

        if not any(lnk in links for lnk in ('prev', 'up', 'next')): # Short circuit
            return

        if 'prev' in links:
            prev = links['prev'][0]
            prev_link = tag.a(prev_label, href=prev['href'], title=prev['title'],
                              class_='prev')

        add_ctxtnav(req, tag.span('', prev_link or prev_label, id='leftarrow',
                                  class_=not prev_link and 'missing' or None))

        if up_label and 'up' in links:
            up = links['up'][0]
            add_ctxtnav(req, tag.a(up_label, href=up['href'], title=up['title']))

        if 'next' in links:
            next_ = links['next'][0]
            next_link = tag.a(next_label, href=next_['href'], title=next_['title'],
                              class_='next')

        add_ctxtnav(req, tag.span(next_link or next_label, '', id='rightarrow',
                                  class_=not next_link and 'missing' or None))

    def filter_navitems(self, elements, req, data):
        data['prevnext'] = []
        prevnext = False
        for elem in elements:
            html = HTML(elem)
            spclasn = str(html.select('@class'))
            clasn = str(html.select('a/@class'))
            if clasn == 'prev' or clasn == 'next' or spclasn == 'missing':
                prevnext = True
            else:
                req.chrome.setdefault('ctxtnav', []).append(elem)
        if prevnext:
            self.prevnext_nav(req, 'Previous', 'Next')

    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        # Ignores empty GIT repository error
        if data is not None and 'display_rev' in data:
            def patch(func):
                def wrap(*args, **kwargs):
                    try:
                        return func(*args, **kwargs)
                    except Exception:
                        # Ignores "NoSuchChangeset: No changeset HEAD in the repository"
                        # This happens with empty GIT repository and causes Source view
                        # to display error message only.
                        pass
                return wrap
            data['display_rev'] = patch(data['display_rev'])

        # Process matching requests based on request path
        if self.is_browser(req, data) and self._is_in_repository(req.path_info):
            self.modify_path_links(req, data)
            if self.is_changeset_available(req, data):
                self.modify_browser(req, data)
        elif self.is_single_changeset(req, data):
            self.modify_changeset_cntxtnav(req, data)
        elif self.is_diff_changeset(req, data) or self.is_prepare_diff(req, data):
            self.modify_diff_changeset_cntxtnav(req, data)
        elif self.is_revision_log(req, data):
            self.modify_maxrows(req, data)
            self.modify_path_links(req, data)
            self.modify_log_cntxtnav(req, data)

        return template, data, content_type

    def modify_changeset_cntxtnav(self, req, data):
        if not data:
            self.log.error('modify_changeset_cntxtnav problem ocurres with path_info: %s args: %s' %
                           (req.path_info, req.args))
            return
        if data['changeset']:
            data['owner'] = get_userstore().getUser(data['changeset'].author)
        ctxtnavitems = req.chrome.pop('ctxtnav', [])
        add_ctxtnav(req, _('All sources'), href = req.href.browser())
        add_ctxtnav(req, _('Last change'))
        add_ctxtnav(req, _('Revision log'), href = req.href.log())
        add_ctxtnav(req, _('Diff changesets'), href = req.href.diff())
        self.filter_navitems(ctxtnavitems, req, data)

    def modify_diff_changeset_cntxtnav(self, req, data):
        req.chrome.pop('ctxtnav', [])
        add_ctxtnav(req, _('All sources'), href = req.href.browser())
        add_ctxtnav(req, _('Last change'), href = req.href.changeset())
        add_ctxtnav(req, _('Revision log'), href = req.href.log())
        add_ctxtnav(req, _('Diff changesets'))

    def modify_log_cntxtnav(self, req, data):
        req.chrome.pop('ctxtnav', [])
        add_ctxtnav(req, _('All sources'), href = req.href.browser())
        add_ctxtnav(req, _('Last change'), href = req.href.changeset())
        add_ctxtnav(req, _('Revision log'))
        add_ctxtnav(req, _('Diff changesets'), href = req.href.diff())

    def modify_browser(self, req, data):
        ctxtnavitems = req.chrome.pop('ctxtnav', [])
        add_ctxtnav(req, _('All sources'))
        prev = False
        for elem in ctxtnavitems:
            html = HTML(elem)
            clasn = str(html.select('a/@class'))
            if clasn == 'prev':
                prev = True
            elif clasn == 'next':
                self.prevnext_ctxnav(req, 'Prev', 'Next', 'Latest Rev')
            elif str(html.select('@class')) == 'missing':
                if prev:
                    self.prevnext_ctxnav(req, 'Prev', 'Next')
            else:
                if str(html.select('text()')).lower() != 'latest revision':
                    req.chrome.setdefault('ctxtnav', []).append(elem)
        add_ctxtnav(req, _("Diff changesets"), _("javascript: applydiff()"))

    def disabled_ctxtnav_links(self, req, data):
        req.chrome.pop('ctxtnav', [])
        add_ctxtnav(req, _('All sources'))
        add_ctxtnav(req, tag.span('Last change', class_ = 'disabled'))
        add_ctxtnav(req, tag.span('Revision log', class_ = 'disabled'))
        add_ctxtnav(req, tag.span('Diff changesets', class_ = 'disabled'))

    def modify_maxrows(self, req, data):
        if data:
            try:
                max = int(req.args.get('max', 20))
                if max < 1:
                    max = 20
                elif max > 200:
                    max = 200
                data['max'] = max
            except ValueError:
                data['max'] = 20

    def modify_path_links(self, req, data):
        if data:
            pathlinks = data.pop('path_links', [])
            links = []
            for link in pathlinks:
                if str(link['name']) == "source:":
                    link['name'] = "Source:"
                links.append(link)
            data['path_links'] = links

    def is_browser(self, req, data):
        return req.path_info.startswith('/browser')

    def _is_in_repository(self, path):
        if path.startswith('/browser'):
            if len(path.split("/")) > 2:
                return True
            else:
                return False
        else:
            return False



    def is_prepare_diff(self, req, data):
        return req.path_info.startswith('/diff')

    def is_revision_log(self, req, data):
        return req.path_info.startswith('/log')

    def is_single_changeset(self, req, data):
        path_correct = req.path_info.startswith('/changeset')
        return path_correct and not self.is_diff_changeset(req, data)

    def is_diff_changeset(self, req, data):
        path_correct = req.path_info.startswith('/changeset')
        return path_correct and data is not None and not 'changeset' in data

    def is_changeset_available(self, req, data):
        if data is None:
            self.log.info('is_changeset_available data is None')
            return False
        rev = req.args.get('rev', '')
        if rev in ('', 'HEAD'):
            rev = None
        srev = data['display_rev'](rev)
        if srev is None or srev == '' or srev == 0:
            self.disabled_ctxtnav_links(req, data)
            return False
        return True


class AnyDiffReplacement(AnyDiffModule):
    """ Disable real browser to prevent getting diff twice
        trac.versioncontrol.web_ui.browser.AnyDiffModule = disabled
    """

    implements(INavigationContributor, IRequestHandler)

    def get_navigation_items(self, req):
        return []

    def get_active_navigation_item(self, req):
        return 'browser'
