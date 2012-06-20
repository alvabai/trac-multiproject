from trac.db import Table, Column, DatabaseManager
# Commont SQL statements

tables = [
  Table('webdav_events')[
    Column('author'),
    Column('time', type = 'integer'),
    Column('method'),
    Column('from'),
    Column('to')
  ]
]

def do_upgrade(env, cursor):
    db_connector, _ = DatabaseManager(env)._get_connector()

    # Create tables
    for table in tables:
        for statement in db_connector.to_sql(table):
            cursor.execute(statement)

    # Set database schema version.
    cursor.execute("INSERT INTO system (name, value) VALUES ('webdav_events_version', '1')")
