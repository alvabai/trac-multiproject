from trac.core import Component, implements
from trac.web.api import IRequestFilter

from multiproject.core.users import get_userstore


class GlobalSessionLocalizer(Component):
    """
    Component for filling up some global session fields
    if they are not set
    """
    implements(IRequestFilter)

    global_fields = ['email', 'name', 'displayname']

    def pre_process_request(self, req, handler):
        """ Fill all global session related fields
        """
        if req.authname == 'anonymous':
            return handler

        # If there are fields missing, update
        for field in self.global_fields:
            if not req.session.has_key(field):
                self.update_user_data(req)
                break
        return handler

    def post_process_request(self, req, template, data, content_type):
        """ This does nothing.. Interface just wants this..
        """
        return template, data, content_type

    def update_user_data(self, req):
        """ Updates all user data into session
        """
        user = get_userstore().getUser(req.authname)

        req.session['email'] = user.mail
        req.session['name'] = user.getDisplayName()
        req.session['displayname'] = user.getDisplayName()
        req.session.save()
