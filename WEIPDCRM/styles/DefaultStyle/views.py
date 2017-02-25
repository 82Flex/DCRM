# coding=utf-8

"""
DCRM - Darwin Cydia Repository Manager
Copyright (C) 2017  WU Zheng <i.82@me.com>

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

Notice: You have used class-based views, that's awesome.
        If not necessary, you can try function-based views.
        You may add lines above as license.
"""

from django.views.generic import ListView, DetailView

from WEIPDCRM.models.version import Version
from WEIPDCRM.models.package import Package


class Index(ListView):
    """
    Notice: Class name should use CamelCase name method.
    """
    model = Package
    context_object_name = 'package_list'
    template_name = 'frontend/index.html'


class PackageView(DetailView):
    """
    Notice: There is no need to override the default get_queryset method,
            because they remained their default behaviour.
    """
    model = Version
    context_object_name = "package_info"
    pk_url_kwarg = 'package_id'
    template_name = 'frontend/package.html'
