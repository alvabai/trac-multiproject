from trac.env import Environment
from multiproject.core.configuration import conf
from multiproject.home.admin.storageusage import StorageUsageNotifier

module = StorageUsageNotifier()
module.notify_now(Environment(conf.getEnvironmentSysPath(conf.sys_home_project_name)))
