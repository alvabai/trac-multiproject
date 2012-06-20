# -*- coding: utf-8 -*-
from multiproject.common.tags.tags import Tags
from multiproject.tests.ConfigurationStub import dbStub
from multiproject.core.test.cqdetestcase import CQDETestCase

class TagsTestCase(CQDETestCase):

    def setUp(self):
        # tag_id, tag_name, tag_count
        dbStub.addResult([
            [1, 'joo', 150],
            [2, 'ei', 30],
            [3, 'kissanviikset', 1]
        ])

    def tearDown(self):
        dbStub.reset()

    def test_build_cloud(self):
        t = Tags()
        data = t.build_cloud()

        self.assertTrue(data)
        self.assertEquals(len(data), 3)
        for row in data:
            self.assertIn(row['name'], ('joo', 'ei', 'kissanviikset'))
            self.assertIn(row['count'], (150, 30, 1))
        # Font size should scale from 8 to 32. List is ordered alphabetically by tag name.
        self.assertTrue(8 < int(data[0]['font_size']) < 32)
        self.assertEquals(int(data[1]['font_size']), 32)
        self.assertEquals(int(data[2]['font_size']), 8)

        self.assertTrue(dbStub.closed)

    def test_build_cloud_empty(self):
        dbStub.reset()
        dbStub.addResult([])
        t = Tags()
        data = t.build_cloud()
        self.assertFalse(data)
        self.assertTrue(dbStub.closed)

    def test_build_project_tags(self):
        t = Tags()
        data = t.build_project_tags(0)

        self.assertTrue(data)
        self.assertEquals(len(data), 3)
        for row in data:
            self.assertIn(row['name'], ('joo', 'ei', 'kissanviikset'))
            self.assertIn(row['count'], (150, 30, 1))

        self.assertTrue(dbStub.closed)

    def test_build_project_tags_empty(self):
        dbStub.reset()
        dbStub.addResult([])
        t = Tags()
        data = t.build_project_tags(0)
        self.assertFalse(data)
        self.assertTrue(dbStub.closed)

    def test_remove(self):
        t = Tags()
        ret = t.remove(1, 'joo')
        self.assertTrue(ret)
        self.assertTrue(dbStub.closed)

    def test_add(self):
        t = Tags()
        ret = t.add(1, 'testi')
        self.assertTrue(ret)
        self.assertTrue(dbStub.closed)

    def test_create(self):
        t = Tags()
        tag_id = t.create('testi')
        self.assertTrue(tag_id)
        self.assertTrue(dbStub.closed)

    def test_tag_id_empty(self):
        dbStub.reset()
        dbStub.addResult([])
        t = Tags()
        tag_id = t.tag_id('testi')
        self.assertEquals(tag_id, None)
        self.assertTrue(dbStub.closed)

    def test_tag_count(self):
        t = Tags()
        tag_count = t.tag_count(0)
        self.assertEquals(tag_count, 1)
        self.assertTrue(dbStub.closed)
