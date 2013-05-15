#!/usr/bin/env python

import os
from mercurial import demandimport; demandimport.enable()
from mercurial.hgweb.hgwebdir_mod import hgwebdir
import mercurial.hgweb.wsgicgi as wsgicgi

target = os.environ['SCRIPT_URL'].split('/')
config = "${trac_repositories_path}/%s/hgweb.config" % target[1]
application = hgwebdir(config)
wsgicgi.launch(application)
