from multiproject.core.cache.project_cache import ProjectCache
from multiproject.core.test.cqdetestcase import CQDETestCase

class DummyProject(object):
    def __init__(self, prj_id):
        self.id = prj_id

class ProjectCacheTestCase(CQDETestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testProjectNameIdCaching(self):
        env_name = "someenvnamethatwontactuallyexist"
        prj_id = 2314
        cache = ProjectCache.instance()
        
        cache.setProjectId(env_name, prj_id)
        self.assertEquals(cache.getProjectId(env_name), prj_id)
        
        cache.clearProjectId(env_name)
        self.assertEquals(cache.getProjectId(env_name), None)
        
    def testProjectObjectCaching(self):
        cache = ProjectCache.instance()
        
        prj_id = 2345
        
        project = DummyProject(prj_id)
        
        cache.setProject(project)
        self.assertEquals(cache.getProject(prj_id).id, prj_id)
        
        cache.clearProject(prj_id)
        self.assertEquals(cache.getProject(prj_id), None)
