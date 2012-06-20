from trac.web.href import Href
import base64

class DummyPermissions(object):
    def __init__(self, req):
        self.req = req
        self.count = 0

    def next(self):
        if self.count >= len(self.req.permissions):
            self.count = 0
            raise StopIteration
        else:
            c = self.count
            self.count = c + 1
            return self.req.permissions[c]

    def __getitem__(self, item):
        return self.req.permissions[item]

    def __iter__(self):
        self.count = 0
        return self

    def require(self, perm):
        if perm not in self.req.permissions:
            raise Exception("Dummy exception")

    def has_permission(self, perm, resource):
        return perm in self.req.permissions

    def __call__(self, realm_or_resource, id=False, version=False):
        return self


class DummyReq(object):
    """ Request class to be used in access tests
        """

    def __init__(self, user, password, method, uri, args, permissions=None):
        if permissions is None:
            permissions = []
        self.user = user
        self.password = password
        self.method = method
        self.uri = uri
        self.href = Href(uri)
        self.base_path = uri
        self.path_info = uri
        self.args = args
        self.perm = DummyPermissions(self)
        self.permissions = permissions
        self.chrome = {'notices': []}

        user_pass = "%s:%s" % (user, password)

        self.headers_in = {'Authorization': "Basic %s" % base64.b64encode(user_pass)}

    def get_basic_auth_pw(self):
        return self.password

    def get_options(self):
        return {}
