# -*- coding: utf-8 -*-
"""
Development/testing tool for generating analytics data with given parameters
Example usage::

    python egenerator.py --user=foo --user=bar --event=release_downloaded --project=testproject 100
    python egenerator.py -u=foo -e=wiki_created -e=file_downloaded -p testproject -p gitproject 10

"""
import sys
import argparse
import random
import logging
from datetime import datetime, timedelta

from multiproject.core.analytics.event import EventLogIO
from multiproject.core.analytics.etl import EventLogETL
from multiproject.core.analytics.etl import SummaryETL


EVENT_DESCRIPTIONS = {
    'wiki_created':'Wiki pages created',
    'wiki_edited':'Wiki pages edited',
    'topic_created':'Discussion topics created',
    'topic_edited':'Discussion topics updated',
    'topic_deleted':'Discussion topics removed',
    'message_created':'Discussion messages posted',
    'ticket_created':'Tickets created',
    'ticket_closed':'Tickets closed',
    'source_checkin':'Source updates',
    'source_checkout':'Source checkouts ',
    'file_uploaded':'Files uploaded',
    'file_downloaded':'Files downloaded',
    'release_uploaded':'Project releases uploaded',
    'release_downloaded':'Project releases downloaded',
    'page_request':'Project page viewed'
}

logging.basicConfig(level=logging.WARNING)


class EventGenerator(object):
    """
    Simple analytical event generator
    """
    def __init__(self):
        self.log = EventLogIO()
        self.etl = EventLogETL()


    def generate(self, count, projects, users, events):
        event = dict()

        for i in xrange(count):
            eventtype = random.choice(events)
            if eventtype not in EVENT_DESCRIPTIONS.keys():
                logging.warning('Event type "%s" is not known, skipping it' % eventtype)
                continue

            event['project'] = random.choice(projects)
            event['event'] = eventtype
            event['username'] = random.choice(users)

            self.log.write_event(event)
            print '.',

        print ''


    def process(self):
        # Update tables
        self.etl.run()

        # Run summaries from last two full hours
        dt_now = datetime.utcnow()
        dt_end = dt_now - timedelta(minutes = dt_now.minute, seconds = dt_now.second, microseconds = dt_now.microsecond)
        dt_start = dt_end - timedelta(hours = 2)

        stl = SummaryETL(dt_start, dt_end)
        stl.run()


def main():
    parser = argparse.ArgumentParser(description='Generates and processes analytical events')
    parser.add_argument('-l', '--list', action='store_true', default=False, help='List available event types')

    ggroup = parser.add_argument_group('generate')
    ggroup.add_argument('-e', '--etype', action='append', type=str, help='Type of events to create. Can be passed multiple times')
    ggroup.add_argument('-u', '--user', action='append', type=str, help='Username who created event. Can be passed multiple times')
    ggroup.add_argument('-p', '--project', action='append', type=str, help='Project identifier to create events to. Can be passed multiple times')
    ggroup.add_argument('-n', '--noprocess', action='store_true', help='Do not process the generated data, only add to queue')
    ggroup.add_argument('count', metavar='COUNT', nargs='?', default=0, type=int, help='Number of events to create')

    args = parser.parse_args()

    if args.list:
        print '\n'.join(sorted(EVENT_DESCRIPTIONS.keys()))
        return sys.exit(0)

    if args.count <= 0:
        print 'Please provide the number of events to create'
        parser.print_help()
        return sys.exit(0)

    eg = EventGenerator()
    eg.generate(count=args.count, events=args.etype, users=args.user, projects=args.project)
    if not args.noprocess:
        eg.process()


if __name__ == '__main__':
    main()
