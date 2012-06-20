"""
Retrieve the timelines from each project and store
"""
from optparse import OptionParser

from multiproject.home.timeline.api import GlobalTimeline
from multiproject.core.cache.timeline_cache import TimelineCache

def main(options):
    """
    :param options: optparse options
    """
    tl = GlobalTimeline()

    # Update last 24 hours for every hour (this makes sure we will not miss any events)
    tl.refresh_today(update=options.update)

    # Clean up old events from the timeline. For now we keep only last 60 days.
    tl.clean_up(days_to_keep = options.days)

    # Clear cache
    cache = TimelineCache()
    cache.clear()

if __name__ == '__main__':
    usage = """
    Retrieves the timelines from each project and store.
    The script is usually run by cron task::

        # Run daily
        0 0 * * python scripts/cron/refresh_timeline.py

    Usage: %prog [options]
    """
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--days-to-keep", dest="days", type=int, default=60,
                      help="Number of days to keep on cleanup", metavar="DAYS")
    parser.add_option("-u", "--update",
                      action="store_true", dest="update", default=False,
                      help="Update existing entries")
    (options, args) = parser.parse_args()

    # Run the app
    main(options)
