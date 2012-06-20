= Fixtures =
This is a default fixture set (basic). Use fixture_loader for loading fixtures into test database.

fixtures.txt says in which order fixtures needs to be loaded at


= Loading fixtures =
# Loads the default basic fixture set
self.load_fixtures()

# If you need/have your own fixture set load it like this
fl = FixtureLoader.instance()
fl.load_all_fixtures('performance_fixtures')

= Creating a new fixture set =
 - Create new folder under fixtures folder and name it as you wish your fixture set to be named.
 - Create csv files having your fixture data
 - Create fixtures.txt file to tell in which order fixtures needs to be loaded in order to not fail fk