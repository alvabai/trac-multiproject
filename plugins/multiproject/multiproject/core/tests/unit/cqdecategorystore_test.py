# -*- coding: utf-8 -*-
from multiproject.core.test.cqdetestcase import CQDETestCase
from multiproject.core.categories import CQDECategoryStore
from ..ConfigurationStub import dbStub

contexts = [
    # context_id, context_name
    [1, "context1"],
    [2, "context2"]
]

contextlist = [
    # context_id, context_name, description
    [1, "context1", "desc1"],
    [2, "context2", "desc2"]
]

categories = [
    # category_id, category_name
    [3, 'cats'],
    [4, 'dogs'],
    [5, 'bugs']
]

cat_list = [
    # category_id, name, description, parent, context
    [3, 'cats', 'Cats', 'desc3', None, 1],
    [4, 'dogs', 'Dogs', 'desc4', None, 1],
    [5, 'bugs', 'Bugs', 'desc5', None, 1]
]

category_tree = [
    # category_id, name, description, parent
    [3, 'cats', 'Cats', None],
    [4, 'dogs', 'Dogs', None],
    [5, 'bugs', 'Bugs', None]
]

subcategories = [
    [6, 'subcat1'],
    [7, 'subcat2']
]

class CQDECategoryStoreTestCase(CQDETestCase):

    def setUp(self):
        pass

    def tearDown(self):
        dbStub.reset()

    def test_bind(self):
        dbStub.addResult([])
        c = CQDECategoryStore()
        self.assertTrue(c.bind_category_project(1, 2))
        self.assertTrue(dbStub.cursors[0].query.lower().startswith("insert into project_categories"))
        self.assertTrue(dbStub.closed)

    def test_unbind(self):
        dbStub.addResult([])
        c = CQDECategoryStore()
        self.assertTrue(c.unbind_category_project(1, 2))
        self.assertTrue(dbStub.cursors[0].query.lower().startswith("delete from project_categories"))
        self.assertTrue(dbStub.closed)

    def test_bind_error(self):
        dbStub.addResult([])
        dbStub.setExceptions(True)
        c = CQDECategoryStore()
        self.assertFalse(c.bind_category_project(1, 2))
        self.assertTrue(dbStub.closed)

    def test_unbind_error(self):
        dbStub.addResult([])
        dbStub.setExceptions(True)
        c = CQDECategoryStore()
        self.assertFalse(c.unbind_category_project(1, 2))
        self.assertTrue(dbStub.closed)

    def test_fetch_selected_categories(self):
        dbStub.addResult(contextlist) # 2 contexts
        dbStub.addResult(cat_list)
        dbStub.addResult([])
        c = CQDECategoryStore()
        data = c.fetch_selected_categories(2)
        self.assertTrue(data)
        self.assertEquals(len(data), 2)
        self.assertEquals(len(data[1]), 3)
        self.assertEquals(len(data[2]), 0)
        self.assertEquals(data[1][0].name, 'cats')
        self.assertEquals(data[1][1].name, 'dogs')
        self.assertEquals(data[1][2].name, 'bugs')
        self.assertTrue(dbStub.closed)

    def test_fetch_selected_categories_error(self):
        dbStub.addResult(contextlist) # 2 contexts
        dbStub.addResult(cat_list)
        dbStub.addResult([])
        dbStub.setExceptions(True)
        c = CQDECategoryStore()
        data = c.fetch_selected_categories(2)
        self.assertFalse(data)
        self.assertTrue(dbStub.closed)

    def test_fetch_available_categories(self):
        dbStub.addResult(categories)
        dbStub.addResult(subcategories)
        dbStub.addResult([]) # end recursion
        c = CQDECategoryStore()
        data = c.fetch_available_categories(1, 2, 3)
        self.assertTrue(data)
        self.assertEquals(len(data), 3)
        self.assertEquals(data[3]['name'], 'cats')
        childs = data[3]['childs']
        self.assertTrue(childs)
        self.assertEquals(len(childs), 2)
        self.assertEquals(childs[6]['name'], 'subcat1')
        self.assertTrue(dbStub.closed)

    def test_fetch_available_categories_error(self):
        dbStub.addResult(categories)
        dbStub.addResult(subcategories)
        dbStub.setExceptions(True)
        c = CQDECategoryStore()
        data = c.fetch_available_categories(1, 2, 3)
        self.assertFalse(data)
        self.assertTrue(dbStub.closed)

    def test_fetch_context_data(self):
        dbStub.addResult(contextlist) # 2 contexts
        dbStub.addResult(category_tree) # 3 categories
        dbStub.addResult([]) # no subcategories for each of the 3 categ.
        dbStub.addResult([])
        dbStub.addResult([])
        dbStub.addResult(subcategories) # 2 project_categories
        dbStub.addResult([])

        c = CQDECategoryStore()
        data = c.fetch_context_data()
        self.assertTrue(data)
        self.assertEquals(len(data), 2)
        self.assertEquals(data[1]['name'], 'context1')
        self.assertEquals(len(data[1]['categories']), 3)
        self.assertTrue(dbStub.closed)

    def test_fetch_context_data_error(self):
        dbStub.addResult(categories)
        dbStub.addResult(subcategories)
        dbStub.setExceptions(True)
        c = CQDECategoryStore()
        data = c.fetch_context_data()
        self.assertFalse(data)
        self.assertTrue(dbStub.closed)
