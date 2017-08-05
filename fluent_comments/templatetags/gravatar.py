import hashlib
import urllib
from django import template
register = template.Library()

# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=128):
    # default image, doc: https://en.gravatar.com/site/implement/images/
    default = 'mm'
    return "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(email.lower()).hexdigest(), urllib.urlencode({'d': default, 's': str(size)}))
