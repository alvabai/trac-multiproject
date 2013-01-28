# -*- coding: utf-8 -*-
class ReqMock(object):
    method = ""
    args = Arguments
    def __init__(self, val):
        self.method = val

class Arguments(Object):
    def get(self, val):
        if(val == "searchprojects"):
            return True
        elif (val == "pattern"):
            return "project"