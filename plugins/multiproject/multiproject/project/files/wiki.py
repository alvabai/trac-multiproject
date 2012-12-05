# -*- coding: utf-8 -*-
from trac.config import Option
from trac.core import Component, implements, TracError
from trac.util import pretty_size
from trac.web.chrome import Chrome, add_script, add_stylesheet
from trac.wiki import IWikiSyntaxProvider, IWikiMacroProvider, parse_args
from trac.util.html import html
from trac.util.translation import _

from multiproject.core.files.api import ProjectDownloadEntry, MappedFileNode
from multiproject.core.users import get_userstore
from multiproject.core.util.util import format_filename
from multiproject.project.files.core import FilesCoreComponent


DOWNLOADS_GLUE_COMPONENT = 'multiproject.project.files.downloadsglue.DownloadsGlue'


class ProjectDownloadsWiki(Component):
    implements(IWikiMacroProvider, IWikiSyntaxProvider)

    macros = {'FilesDownloadsCount': """Display the count of files downloads.
Also the downloads which have been deleted are counted in.""",
              'FilesDownloadsNarrow': """Display a narrow list of files downloads.
Default is to not show anything when there are no downloads.
Optional params:

- no_hide: If no_hide is given, shows a text "No files downloads" instead.
- title: h2 title for the downloads. If not given, default title is shown.
- only_featured: Show only featured downloads

Example usages:
{{{
[[FilesDownloadsNarrow]]
[[FilesDownloadsNarrow(no_hide=True)]]
[[FilesDownloadsNarrow(title=My title, only_featured=True)]]
}}}
""",
              'FilesDownloads': """Display a list of files downloads.
Default is to not show anything when there are no downloads.
Optional params:

- no_hide: If no_hide is given, shows a text "No files downloads" instead.
- title: h2 title for the downloads. If not given, default title is shown.
- only_featured: Show only featured downloads

Example usages:
{{{
[[FilesDownloads]]
[[FilesDownloads(no_hide=True)]]
[[FilesDownloads(title=My title, only_featured=True)]]
}}}
"""}

    override_download_links = Option('multiproject-files', 'override_download_link',
        default='True',
        doc="""Whether or not to override download links, if the DownloadsGlue component is not enabled.
Can be useful to set to False, if other than multiproject components are using that.""")

    def get_macros(self):
        for macro in self.macros:
            yield macro

    def get_macro_description(self, name):
        return self.macros.get(name)

    def expand_macro(self, formatter, name, content, args=None):

        # Parse optional arguments
        if args is None:
            args = parse_args(content)
            if len(args) > 1:
                args = args[1]

        files_core = FilesCoreComponent(self.env)
        node_factory, download_config = files_core.files_node_factory_and_config(formatter.req)
        if 'FILES_DOWNLOADS_VIEW' not in formatter.req.perm:
            return ''

        if name == 'FilesDownloadsCount':
            count = ProjectDownloadEntry.total_download_count(node_factory.project_id)
            return html.span(count, class_="files_downloads_count")
        elif name == 'FilesDownloads' or name == 'FilesDownloadsNarrow':
            is_narrow = True
            if name == 'FilesDownloads':
                is_narrow = False

            no_hide = False
            if args.has_key('no_hide') and args['no_hide'].lower() == 'true':
                no_hide = True

            only_featured = False
            if args.has_key('only_featured') and args['only_featured'].lower() == 'true':
                only_featured = True

            title = _('Featured downloads') if only_featured else _('Downloads')
            try:
                title = _(args['title'])
            except KeyError:
                title = _('Featured downloads') if only_featured else _('Downloads')
            except ValueError as e:
                title = _('Invalid title: %(reason)s', reason=str(e))

            download_entries = ProjectDownloadEntry.get_all_download_entries(node_factory.project_id,
                only_featured=only_featured)

            downloads = []
            user_store = None
            user_by_id = {}
            if not is_narrow:
                user_store = get_userstore()

            for download_entry in download_entries:
                if not is_narrow and not user_by_id.has_key(download_entry.uploader_id):
                    user = user_store.getUserWhereId(download_entry.uploader_id)
                    user_by_id[download_entry.uploader_id] = user

                # This doesn't check whether the node really exists
                node = MappedFileNode.from_download_entry(download_entry, node_factory)
                downloads.append(node)

            add_stylesheet(formatter.req, 'multiproject/css/files.css')
            add_script(formatter.req, 'multiproject/js/files.js')

            return Chrome(self.env).render_template(formatter.req,
                'multiproject_files_wiki.html',
                    {'downloads' : downloads,
                     'downloads_dir': download_config.downloads_dir,
                     'is_narrow': is_narrow,
                     'no_hide': no_hide,
                     'only_featured': only_featured,
                     'user_by_id': user_by_id,
                     'title': title,
                     'format_filename': format_filename},
                'text/html', True)

    # IWikiSyntaxProvider

    def get_link_resolvers(self):
        # We allow this to be configurated, so that the "download:example.txt" links can work by
        # other means also.
        if not self.env.is_component_enabled(DOWNLOADS_GLUE_COMPONENT) and self.override_download_links:
            yield ('download', self.file_link)
        yield ('filesdownload', self.file_link)
        yield ('file', self.file_link)

    def get_wiki_syntax(self):
        return []

    def file_link(self, formatter, ns, target, label):
        req = formatter.req

        if ns != 'file' and ns != 'download' and ns != 'filesdownload':
            return

        files_core = FilesCoreComponent(self.env)
        node_factory, download_config = files_core.files_node_factory_and_config(req)
        try:
            if ns == 'file':
                node = MappedFileNode.from_path(target, node_factory, True)
            else:
                node = MappedFileNode.from_download_path(target, node_factory, True)
            missing_perm = None
            if node.is_download():
                if 'FILES_DOWNLOADS_VIEW' not in req.perm:
                    missing_perm = 'FILES_DOWNLOADS_VIEW'
            elif 'FILES_VIEW' not in req.perm:
                missing_perm = 'FILES_VIEW'
            if missing_perm:
                return html.a(label, href='#',
                    title = _('Missing %(permission)s permission', permission=missing_perm),
                        class_ = 'missing')
            if node.exists():
                if node.is_file():
                    if node.is_download():
                        if not node.download().is_available():
                            return html.a(label, href='#',
                                title = _('Download information not available for %(path)s',
                                    path=node.relative_path),
                                class_ = 'missing')
                        else:
                            return html.a(label, href=node.get_url(req),
                                title = _('Download %(name)s (%(size)s)',name=node.filename,
                                    size= pretty_size(node.size)))
                    else:
                        return html.a(label, href=node.get_url(req),
                            title = _('File %(name)s',name=node.filename))
                elif node.is_dir():
                    return html.a(label, href=node.get_url(req),
                        title = _('Folder %(name)s',name=node.filename))
            else:
                return html.a(label, href='#',
                    title = _('Not existing file: %(path)s', path=node.relative_path),
                    class_ = 'missing')
        except TracError:
            # File doesn't exist
            return html.a(label, href='#',
                title=_('Invalid target for %(ns)s: %(path)s',ns=ns, path=target),
                class_='missing')
