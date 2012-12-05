import re

from trac.config import ListOption, Option
from trac.core import Component, implements
from trac.web import IRequestFilter

from multiproject.core.configuration import conf


class ChromeHrefItemsReplacement(list):
    """
    This is used instead of req.chrome['scripts'] and req.chrome['links']['stylesheet'] lists.
    Also, data.chrome['late_scripts'] list is provided through this class as a view,
    and data.chrome['late_links']['stylesheet'] after site_macros.html is included.
    Using this instead of list just modifies the iteration of list so that
    when items are iterated, chrome_url is replaced with the static_htdocs_location + '/'.
    Using set_viewed_list makes the iteration to use the given list.
    """

    def __init__(self, chrome_url, regexp,
                 static_htdocs_location, seq=()):
        """
        The chrome_url should end with '/' and static_htdocs_location should not end with '/'.
        :param regexp: re.compile(r"^({0})/".format('|'.join(static_htdocs_plugin_dirs))) or '*'
        """
        self.chrome_url = chrome_url
        self.static_htdocs_location = static_htdocs_location

        self.regexp = regexp

        self.viewed_list = None

        super(ChromeHrefItemsReplacement, self).__init__(seq)

    def __iter__(self):
        if self.viewed_list is not None:
            list_iter = self.viewed_list.__iter__()
        else:
            list_iter = super(ChromeHrefItemsReplacement, self).__iter__()
        for item in list_iter:
            href = item['href']
            if href.startswith(self.chrome_url):
                href = href[len(self.chrome_url):]
                if self.regexp == '*' or self.regexp.match(href):
                    new_item = item.copy()
                    new_href = '{0}/{1}'.format(self.static_htdocs_location, href)
                    new_item['href'] = new_href
                    yield new_item
                    continue
            # if not done, yield item
            yield item

    def set_viewed_list(self, other_list):
        """
        If this method is used, when self is iterated, the other_list is iterated instead.
        :param other_list:
        :return:
        """
        self.viewed_list = other_list


class GlobalStaticRequestFiles(Component):

    implements(IRequestFilter)

    static_htdocs_plugin_dirs = ListOption('multiproject', 'static_htdocs_plugin_dirs', default=['*'],
        doc='List of global, static htdocs plugin directories, like "multiproject", '
        'whose urls are manipulated.')

    static_htdocs_location = Option('multiproject', 'static_htdocs_location', default='',
        doc='Like htdocs_location, but for plugin htdocs. '
        'Multiproject files are located under ${htdocs_location}/multiproject/.')

    def __init__(self):
        if not self.static_htdocs_plugin_dirs or not self.static_htdocs_location:
            return

        base_url = self.config.get('multiproject', 'url_projects_path', '/')
        base_url = base_url.rstrip('/') # base_url '/' will be ''
        self.chrome_url = "{0}/{1}/chrome/".format(base_url, conf.resolveProjectName(self.env))

    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        if not self.static_htdocs_plugin_dirs or not self.static_htdocs_location:
            # Don't change the
            return template, data, content_type

        # Setup chrome['scripts'] and chrome['links']['stylesheet'] for the templates.
        static_htdocs_location = self.static_htdocs_location
        if static_htdocs_location.endswith('/'):
            static_htdocs_location = static_htdocs_location.rstrip('/')

        existing_links = req.chrome.setdefault('links', {})
        existing_stylesheets = existing_links.get('stylesheet', [])
        existing_scripts = req.chrome.get('scripts', [])

        if len(self.static_htdocs_plugin_dirs) == 1 and self.static_htdocs_plugin_dirs[0] == '*':
            regexp = '*'
        else:
            regexp = re.compile(r"^({0})/".format('|'.join(self.static_htdocs_plugin_dirs)))

        existing_links['stylesheet'] = ChromeHrefItemsReplacement(self.chrome_url,
            regexp, self.static_htdocs_location, existing_stylesheets)
        req.chrome['scripts'] = ChromeHrefItemsReplacement(self.chrome_url,
            regexp, self.static_htdocs_location, existing_scripts)

        chrome_url = self.chrome_url

        def setup_late_scripts_and_stylesheets(chrome):
            """
            Function for setting data['chrome']['late_links']['stylesheet']
            and data['chrome']['late_scripts'] before they are used.
            This method is invoked from site_macros.html.
            We cannot directly set them in post_process_request, since
            they would be overriden in the Chrome.render_template.
            :param chrome: a dict corresponding data['chrome']
            """
            existing_late_stylesheets = chrome.setdefault('late_links', {}).get('stylesheet', [])
            late_scripts_view = ChromeHrefItemsReplacement(chrome_url,
                regexp, static_htdocs_location)
            late_scripts_view.set_viewed_list(chrome.setdefault('late_scripts', []))
            chrome['late_scripts'] = late_scripts_view
            # we replace the stylesheet list in the late_links, thus we don't setup the view
            chrome['late_links']['stylesheet'] = ChromeHrefItemsReplacement(chrome_url,
                regexp, static_htdocs_location, existing_late_stylesheets)
            del chrome['setup_late_scripts_and_stylesheets']

        req.chrome['setup_late_scripts_and_stylesheets'] = setup_late_scripts_and_stylesheets

        return template, data, content_type
