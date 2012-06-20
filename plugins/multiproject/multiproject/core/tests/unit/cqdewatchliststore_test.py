# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.core.watchlist import CQDEWatchlistStore
from ..ConfigurationStub import conf

class CQDEWatchlistStoreTestCase(CQDETestCase):

    def setUp(self):
        conf.use_test_db(True)
        self.load_fixtures()
        conf.memcached_enabled = False

    def tearDown(self):
        conf.use_test_db(False)

    def test_watch(self):
        w = CQDEWatchlistStore()
        self.assertTrue(w)
        w.watch_project(32, 23)
        w.watch_project(34, 23, "daily")

        watchlist = w.get_projects_by_user(32)
        self.assertTrue(len(watchlist) == 1)
        self.assertTrue(watchlist[0].user_id == 32)
        self.assertTrue(watchlist[0].project_id == 23)
        self.assertTrue(watchlist[0].notification == "immediate")

        watchlist = w.get_watchers_by_project(23)
        self.assertTrue(len(watchlist) == 2)
        self.assertTrue(w.is_watching(32, 23))
        self.assertTrue(w.is_watching(34, 23))

    def test_unwatch(self):
        w = CQDEWatchlistStore()
        w.watch_project(32, 23, "immediate")
        w.watch_project(34, 23, "daily")

        w.unwatch_project(32, 23)

        watchlist = w.get_projects_by_user(32)
        self.assertTrue(len(watchlist) == 0)
        watchlist = w.get_projects_by_user(34)
        self.assertTrue(len(watchlist) == 1)

        watchlist = w.get_watchers_by_project(23)
        self.assertTrue(len(watchlist) == 1)
        self.assertFalse(w.is_watching(32, 23))

    def test_get_by_notification(self):
        w = CQDEWatchlistStore()
        w.watch_project(32, 23, "immediate")
        w.watch_project(34, 23, "daily")

        watchlist = w.get_by_notification("daily")
        self.assertTrue(len(watchlist) == 1)
        self.assertTrue(watchlist[0].user_id == 34)

        watchlist = w.get_by_notification("weekly")
        self.assertTrue(len(watchlist) == 0)
