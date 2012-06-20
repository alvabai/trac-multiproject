from trac.core import Component, implements
from trac.web.api import ITemplateStreamFilter
from genshi.filters.transform import Transformer
from genshi.builder import Element

class TimelineEmptyMessage(Component):
    implements(ITemplateStreamFilter)

    def filter_stream(self, req, method, filename, stream, data):
        if filename == 'timeline.html':
            if not data['events']:
                return stream | Transformer('//form[@id="prefs"]').before(Element('p')('No events match your search criteria, change the parameters and try again'))
        return stream
