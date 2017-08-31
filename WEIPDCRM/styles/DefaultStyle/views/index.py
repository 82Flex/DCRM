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

from __future__ import unicode_literals

from django.views.generic import ListView
from django.views.decorators.clickjacking import xframe_options_exempt
from WEIPDCRM.models.package import Package
from WEIPDCRM.models.build import Build


class IndexView(ListView):
    """
    Notice: Class name should use CamelCase name method.
            Changed model to Package because it should list all
            enabled package and the latest version control once only.
    """
    allow_empty = True
    paginate_by = 24
    ordering = '-id'
    model = Package
    context_object_name = 'package_list'
    template_name = 'index.html'

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Merge global settings to current context
        """
        context = super(IndexView, self).get_context_data(**kwargs)
        context['url_name'] = "index_page"
        context['packages_num'] = Package.objects.all().count()
        latest_build = Build.objects.order_by('-created_at')
        if latest_build:
            context['release_lastest_updated'] = latest_build[0].created_at
        else:
            context['release_lastest_updated'] = None

        return context
