# -*- coding: utf-8 -*-

def do_upgrade(env, cursor):
    # Create indices for webdav_events times.
    cursor.execute("CREATE INDEX webdav_time_idx "
                   "ON webdav_events (time)")

    # Set database schema version.
    cursor.execute("UPDATE system "
                   "SET value = '2' "
                   "WHERE name = 'webdav_events_version'")
