# ensure some logging initialization
import logging
logging.basicConfig()
from multiproject.core.analytics.etl import EventLogETL

etl = EventLogETL()
etl.run()
