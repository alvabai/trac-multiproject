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
        self.organization_keys = []
        self.authentication_key = 1 # local user

    def getDisplayName(self):
        return self.username

    def createIcon(self, icon):
        pass

    def get_status(self):
        return 'active'

    def isProjectBrowsingAllowed(self):
        return True

    def can_create_project(self):
        return True


class UserStoreStub(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.user = UserStub()
        self.userexists = True
        self.all_users = None

    def getUser(self, username):
        if self.userexists:
            return self.user
        return None

    def getUserWhereId(self, id):
        return self.getUser(None)

    def storeUser(self, user):
        return True

    def updateUser(self, user):
        return True

    def deleteUser(self, user):
        return True

    def userExists(self, username, password=None):
        return self.userexists

    def updatePassword(self, user, password):
        return True

    def get_user_initials(self):
        return [], {}

    def get_all_users(self, limit, count, initial):
        return self.all_users

    def query_users(self, query):
        return self.all_users

    def getMemberCountInProjects(self):
        return 6
