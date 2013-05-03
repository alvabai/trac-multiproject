#!/bin/sh
# convert multiproject imports with sed
/^from multiproject.core.configuration import conf\s*$/{s/import conf/import Configuration/;
a\
conf = Configuration.instance()
}

