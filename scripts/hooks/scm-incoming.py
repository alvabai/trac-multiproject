# Generic script for all source control management incoming hooks

import sys
from multiproject.core.analytics.event import EventLogIO
from datetime import datetime
event_log = EventLogIO()

script, repo_path, author = sys.argv

event_log.write_event({'username':author,
                       'project':repo_path.split("/")[-3],
                       'timestamp':datetime.utcnow(),
                       'event':'source_checkin'
                       })
