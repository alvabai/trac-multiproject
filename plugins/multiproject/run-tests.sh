#!/bin/sh
nosetests -v --with-xunit --xunit-file=../../nosetests.xml multiproject/core/util/test \
multiproject/test
