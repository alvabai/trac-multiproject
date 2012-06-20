from trac.versioncontrol.web_ui.browser import BrowserModule
from trac.util.translation import _
from genshi.builder import tag

_TRUE_VALUES = ('yes', 'true', 'enabled', 'on', 'aye', '1', 1, True)

class BrowserToSource(BrowserModule):
    """ Disable real browser to prevent getting browser twice
        
        trac.versioncontrol.web_ui.browser.BrowserModule = disabled
    """
    def __init__(self):
        BrowserModule.__init__(self, self.compmgr)
    
    def get_navigation_items(self, req):
        for category, name, text in \
                        BrowserModule.get_navigation_items(self, req):
            if str(text) == str(tag.a(_('Browse Source'), href=req.href.browser())):
                yield (category, name, tag.a('Source', href=req.href.browser()))

