import hashlib
import urllib
from django import template
from django.contrib.sites.models import Site
from django.conf import settings

register = template.Library()

# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=40):
    current_site = Site.objects.get(id=settings.SITE_ID)
    default = current_site.domain + "/static/frontend/img/default_avatar.png"
    return "https://www.gravatar.com/avatar/%s?%s" % (hashlib.md5(email.lower()).hexdigest(), urllib.urlencode({'d': default, 's': str(size)}))
