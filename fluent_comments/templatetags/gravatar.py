import hashlib
import urllib
from django import template
from DCRM.settings import LANGUAGE_CODE
register = template.Library()

# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=128):
    # Optimize for Chinese
    url = "https://cdn.v2ex.com/gravatar/" if LANGUAGE_CODE == 'zh-hans' else "https://www.gravatar.com/avatar/"
    # default image, doc: https://en.gravatar.com/site/implement/images/
    default = 'mm'
    return url + "%s?%s" % (hashlib.md5(email.lower()).hexdigest(), urllib.urlencode({'d': default, 's': str(size)}))
