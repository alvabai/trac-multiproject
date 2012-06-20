from multiproject.core.decorators import singleton

@singleton
class CQDESysPath(object):

    # List all dirs here
    sys_dir = {
                'sys_root': '/',
                'dav': '/webdav',
                'projects': '/projects',
                'repositories': '/repositories',
                'theme': '/dist/current/theme',
                'logs': '/logs',
                'analytics': '/analytics',
                'analytics_failed': '/analytics/failed',
                'analytics_faildump': '/analytics/fail_dump',
                'analytics_archived': '/analytics/archived',
                'dist': '/dist',
                'config': '/conf',
                'downloads': '/downloads',
                'results' : '/results',
                'trac_htdocs': '/trac_htdocs',
                'gitosis_admin_repo': '/repositories/gitosis-admin.git',
                'gitosis_clone':'gitosis_clone_tmp/',
                'archive': '/archive',
                'theme_resources': '/storage/trac/themes/res_files/',
                'scm_hooks':'/dist/current/scripts/'
                }

    # List all files here
    sys_file = {'analytics_log' : sys_dir['logs'] + '/analytics.log',
                'application_log': sys_dir['logs'] + '/cqde.log',
                'project_conf' : sys_dir['config'] + '/project.ini',
                'home_conf' : sys_dir['config'] + '/home.ini',
                'storage_usage' : sys_dir['results'] + '/storageusage.csv',
                'storage_notifications' : sys_dir['results'] + '/notifications.csv'
                }

    def __init__(self):
        from multiproject.core.configuration import conf
        self.sys_root = conf.sys_root

        self.sys_paths = {}
        self.sys_paths.update(self.sys_dir)
        self.sys_paths.update(self.sys_file)

    def __getattr__(self, name):
        if name in self.sys_paths:
            return self.sys_root + self.sys_paths[name]
        raise AttributeError

    def list_missing(self):
        """ List missing paths (use build_missing to build them)
        """
        # FIXME: A stub
        pass

    def build_missing(self):
        """ Created all missing system directories
        """
        # FIXME: A stub
        pass

syspath = CQDESysPath()
