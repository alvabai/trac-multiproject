class DummyLog(object):
    def info(self, str):
        pass

    def error(self, str):
        pass

    def debug(self, str):
        pass


class DummyEnv(object):
    def __init__(self, req):
        self.log = DummyLog()
        self.req = req
        self.path = req.uri
        self.project_name = self.path.split('/')[-1]
