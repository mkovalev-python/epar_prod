__author__ = 'Tonakai'
from django.template import Library
from django.template.defaultfilters import linebreaksbr
import re
register = Library()
@register.filter(name='htmlemail')
def htmlemail(value):
    def links_wrap(match):
        text = str(match.group(1)) + str(match.group(2))
        link = text
        if len(text) >= 35:
            text = text[:32] + '...'
        return "<a href='" + link + "' target='_blank'>" + text + "</a>"
    quote_filter = re.compile(r'\[Q\](.+?)\[/Q\]', re.IGNORECASE and re.MULTILINE and re.S)
    value = quote_filter.sub(r'<blockquote class="well">\1</blockquote>', value)
    value = re.sub(r'(http|www\.)([^\ ^\,\r\n\"]+)', links_wrap, value)
    value = re.sub(r'\t', '&nbsp;&nbsp;&nbsp;&nbsp;', value)
    value = linebreaksbr(value)
    return value
