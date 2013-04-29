from trac.env import Environment
from multiproject.core.configuration import Configuration
from multiproject.home.admin.storageusage import StorageUsageNotifier

conf = Configuration.instance()
module = StorageUsageNotifier()
module.notify_now(Environment(conf.getEnvironmentSysPath(conf.sys_home_project_name)))
