# -*- coding: utf-8 -*-

from userTest import *
from dbTest import *

class CQDEUserGroupStoreStub(object):

    def remove_user_from_group(self, user_name, group_name):
        return_val = True
        userstore = get_userstore()
        user = userstore.getUser(user_name)
        if not user:
            return_val = False
        group_id = self.get_group_id(group_name)
        if group_id is None:
            return_val = False
        if return_val == True:
            if user.id == 1 and group_id == 2:
              return_val = True
        return (return_val and admin_query())

    def get_group_id(self, group_name):
        if(group_name == "project1"):
            return 2
        else:
            return None