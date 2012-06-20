#!/usr/bin/env python

# enable importing on demand to reduce startup time
from mercurial import demandimport; demandimport.enable()

from mercurial.hgweb.hgweb_mod import hgweb
import mercurial.hgweb.wsgicgi as wsgicgi

application = hgweb("/path/to/repo", "repository name")
wsgicgi.launch(application)
  
  
