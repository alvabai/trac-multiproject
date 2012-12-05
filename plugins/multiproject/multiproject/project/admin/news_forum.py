# -*- coding: utf-8 -*-
from trac.core import Component, implements, Interface, ExtensionPoint
from trac.admin.api import IAdminPanelProvider

from multiproject.common.wiki.news import ProjectNews
from multiproject.common.projects import Project
from multiproject.core.permissions import CQDEUserGroupStore


class IAnnouncementAdminListener(Interface):
    """
    Extension point interface for components that require notification
    when announcement visibility settings have been changed.
    """

    def announcements_hidden(self):
        """
        Called when announcements are hidden.
        """
        pass

    def announcements_visible(self):
        """
        Called when announcements are set visible.
        """
        pass


class NewsForumAdminPanel(Component):
    """ Trac admin panel component for announcements
    """
    implements(IAdminPanelProvider)

    # Extension points
    announcement_admin_listeners = ExtensionPoint(IAnnouncementAdminListener)

    # IAdminPanelProvider interface requirement
    def get_admin_panels(self, req):
        """ Admin panel navigation items
        """

        if 'TRAC_ADMIN' in req.perm:
            yield ('general', 'General', 'announcements', 'Announcements')


    # IAdminPanelProvider interface requirement
    def render_admin_panel(self, req, cat, page, path_info):
        """ Renders announcements admin panel
        """
        req.perm.require('TRAC_ADMIN')

        showforum = self.config.getbool('discussion', 'show_news_forum', True)

        project = Project.get(self.env)
        groupstore = CQDEUserGroupStore(project.trac_environment_key)
        (public_exists, allowed) = self.get_announce_allowed(groupstore)

        if req.method == 'POST':
            if 'hideforum' in req.args:
                self.config.set('discussion', 'show_news_forum', 'false')
                self.config.save()
                showforum = False
                # Notify listeners
                for listener in self.announcement_admin_listeners:
                    listener.announcements_hidden()
            elif 'showforum' in req.args:
                self.config.set('discussion', 'show_news_forum', 'true')
                self.config.save()
                showforum = True
                # Notify listeners
                for listener in self.announcement_admin_listeners:
                    listener.announcements_visible()
            elif 'allow' in req.args:
                #Allow should add the DISCUSSION_ANNOUNCE_APPEND to the "public contributors" group.
                groupstore.grant_permission_to_group("Public contributors", "DISCUSSION_ANNOUNCEAPPEND")
                (public_exists, allowed) = self.get_announce_allowed(groupstore)
            elif 'disallow' in req.args:
                #Disallow remove it.
                groupstore.revoke_permission_from_group("Public contributors", "DISCUSSION_ANNOUNCEAPPEND")
                (public_exists, allowed) = self.get_announce_allowed(groupstore)
            elif 'rename' in req.args:
                news = ProjectNews(project.env_name)
                news.rename_news_forum(req.args.get('forumname'))

        data = {}
        data['showforum'] = showforum
        data['allowed'] = allowed
        data['public_exists'] = public_exists
        return 'admin_news_forum.html', data

    def get_announce_allowed(self, groupstore):
        public_exists = False
        grp_perms = groupstore.get_all_group_permissions()
        for grpperm in grp_perms:
            self.log.debug(str(grpperm))
            grp, perm = grpperm
            if grp == "Public contributors":
                public_exists = True
                if perm == "DISCUSSION_ANNOUNCEAPPEND":
                    return public_exists, True
        return public_exists, False
