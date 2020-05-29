"""
DCRM - Darwin Cydia Repository Manager
Copyright (C) 2017  WU Zheng <i.82@me.com> & 0xJacky <jacky-943572677@qq.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import hashlib
from urllib.parse import urlencode
from django import template
from DCRM.settings import LANGUAGE_CODE
register = template.Library()

# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=128):
    # Optimize for Chinese
    url = "https://cdn.v2ex.com/gravatar/" if LANGUAGE_CODE == 'zh-Hans' else "https://www.gravatar.com/avatar/"
    # default image, doc: https://en.gravatar.com/site/implement/images/
    default = 'mm'
    return url + "%s?%s" % (hashlib.md5(email.lower().encode()).hexdigest(), urlencode({'d': default, 's': str(size)}))
