# -*- coding: utf-8 -*-
"""
Analytics event tracker for Trac discussion plugin. Listens to Topic and Message
events from Trac discussion plugin and saves them to database.
"""
from trac.core import Component, implements

from multiproject.core.analytics.event import EventLogIO


try:
    from tracdiscussion.listeners import ITopicChangeListener, IMessageChangeListener

    class DiscussionAnalytics(Component):
        implements(ITopicChangeListener, IMessageChangeListener)

        def __init__(self):
            self.env_name = self.env.path.split('/')[-1]

        # TopicChangeListener
        def topic_created(self, context, topic):
            log = EventLogIO()
            event = {}
            event['event'] = "topic_created"
            event['project'] = self.env_name
            event['username'] = context.req.authname
            event['forum_id'] = topic['forum']
            log.write_event(event)

        def topic_changed(self, context, topic, old_topic):
            log = EventLogIO()
            event = {}
            event['event'] = "topic_edited"
            event['project'] = self.env_name
            event['username'] = context.req.authname
            event['forum_id'] = old_topic['forum']
            log.write_event(event)

        def topic_deleted(self, context, topic):
            log = EventLogIO()
            event = {}
            event['event'] = "topic_deleted"
            event['project'] = self.env_name
            event['username'] = context.req.authname
            event['forum_id'] = topic['forum']
            log.write_event(event)

        def message_created(self, context, message):
            log = EventLogIO()
            event = {}
            event['event'] = "message_created"
            event['project'] = self.env_name
            event['username'] = context.req.authname
            event['forum_id'] = message['forum']
            log.write_event(event)

        def message_changed(self, context, message, old_message):
            log = EventLogIO()
            event = {}
            event['event'] = "message_edited"
            event['project'] = self.env_name
            event['username'] = context.req.authname
            event['forum_id'] = old_message['forum']
            log.write_event(event)

        def message_deleted(self, context, message):
            log = EventLogIO()
            event = {}
            event['event'] = "message_deleted"
            event['project'] = self.env_name
            event['username'] = context.req.authname
            event['forum_id'] = message['forum']
            log.write_event(event)

except ImportError:
    class DiscussionAnalytics(Component):
        pass
