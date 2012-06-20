class CursorStubEx(object):
    def __init__(self, result1, result2):
        self.result = [result1, result2]
        self.query = []
        self.closed = False
        self.result_iter = None
        self.exception = False
        self.rnd = -1

    def round(self):
        if self.rnd >= 0:
            return self.rnd
        else:
            return 0

        # Cursor API

    def queryCommand(self, pos=0):
        return self.query[pos].lower()

    def close(self):
        self.closed = True

    def execute(self, query, args=None):
        self.rnd += 1
        self.result_iter = None
        assert not self.closed
        if args is not None:
            query = query % args
        self.query.append(query)
        if self.exception:
            raise Exception

    def fetchall(self):
        assert not self.closed
        return self.result[self.round()]

    def fetchone(self):
        assert not self.closed
        if not self.result_iter:
            self.result_iter = iter(self.result[self.round()])
        try:
            return self.result_iter.next()
        except StopIteration:
            return None

    def __iter__(self):
        return iter(self.fetchone)

    def callproc(self, name, args):
        return True


class CursorStub(object):
    def __init__(self):
        self.result = []
        self.query = None
        self.closed = False
        self.result_iter = None
        self.exception = False

    # Cursor API

    def queryCommand(self, pos=0):
        if self.query:
            return self.query.lower()
        else:
            return None

    def close(self):
        self.closed = True

    def execute(self, query, args=None):
        assert not self.closed
        if args is not None:
            query = query % args
        self.query = query
        if self.exception:
            raise Exception

    def fetchall(self):
        assert not self.closed
        return self.result

    def fetchone(self):
        assert not self.closed
        if not self.result_iter:
            self.result_iter = iter(self.result)
        try:
            return self.result_iter.next()
        except StopIteration:
            return None

    def __iter__(self):
        return iter(self.fetchone)

    def callproc(self, name, args):
        return True


class DatabaseStub(object):
    def __init__(self):
        self.reset()

    def reset(self):
        self.cursors = []
        self.closed = False
        self.committed = False
        self.rollbacked = False
        self.currentcursor = 0

    def addResult(self, result, result2=None):
        if result2:
            self.cursors.append(CursorStubEx(result, result2))
        else:
            self.cursors.append(CursorStub())
            self.cursors[-1].result = result

    def setExceptions(self, onoff):
        for c in self.cursors:
            c.exception = onoff

    # Database API

    def cursor(self, cursortype=None):
        assert not self.closed
        assert self.cursors
        index = self.currentcursor
        if self.currentcursor < len(self.cursors) - 1:
            self.currentcursor += 1
        else: # re-use last cursor
            self.cursors[index].closed = False
            self.cursors[index].result_iter = None
        return self.cursors[index]

    def commit(self):
        assert not self.closed
        self.committed = True

    def rollback(self):
        assert not self.closed
        self.rollbacked = True

    def close(self):
        self.closed = True
