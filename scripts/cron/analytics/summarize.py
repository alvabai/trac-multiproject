from multiproject.core.analytics.etl import SummaryETL
from datetime import datetime, timedelta

# Run summaries from last two full hours
dt_now = datetime.utcnow()
dt_end = dt_now - timedelta(minutes = dt_now.minute, seconds = dt_now.second, microseconds = dt_now.microsecond)
dt_start = dt_end - timedelta(hours = 2)

etl = SummaryETL(dt_start, dt_end)
etl.run()
