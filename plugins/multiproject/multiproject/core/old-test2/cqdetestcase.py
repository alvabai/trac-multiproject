import unittest
from multiproject.core.test.fixtures.fixture_loader import FixtureLoader

class CQDETestCase(unittest.TestCase):
    def load_fixtures(self):
        """ Loads all the test fixtures in a path
        """
        fl = FixtureLoader.instance()
        fl.load_all_fixtures('basic')
    
    def assertIn(self, value, iterable, msg = None):
        if not value in iterable:
            raise self.failureException, \
                  (msg or '%r is not in %r' % (value, iterable))
    
    def assertNotIn(self, value, iterable, msg = None):
        if value in iterable:
            raise self.failureException, \
                  (msg or '%r is in %r' % (value, iterable))
