

def get_userstore():
    """
    Returns the active userstore.
    Currently only MySqlUserStore is supported

    >>> from multiproject.core.users import get_userstore
    >>> userstore = get_userstore()
    >>> userstore.getUser('username')

    :returns: User store
    :rval: MySqlUserStore
    """
    return MySqlUserStoreStub()

class UserStub(object):
    def __init__(self):
        self.id = None
        self.username = None
        self.password = None
        self.pwHash = None
        self.mail = None
        self.mobile = None
        self.givenName = None
        self.lastName = None
        self.icon = None
        self.authentication_key = None
        self.status = None
        self.last_login = None
        self.created = None
        self.expires = None
        self.author_id = None
        self.preferences = {}
        self.organization_keys = []

class MySqlUserStoreStub():
    def getUser(self, username):
        user = UserStub()
        if username == "tero.test":
            user.id = 1
            user.username = username
            user.givenName = "Tero"
            user.lastName = "Testi"
            return user
        else:
            return None

