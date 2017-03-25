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

from django.views.generic import DetailView
from WEIPDCRM.models.version import Version
from WEIPDCRM.models.section import Section

from preferences import preferences
from django.contrib.sites.models import Site

class PackageView(DetailView):
    """
    Notice: There is no need to override the default get_queryset method,
            because they remained their default behaviour.
    """
    model = Version
    context_object_name = 'package_info'
    pk_url_kwarg = 'package_id'
    template_name = 'frontend/package.html'

    def get(self, request, *args, **kwargs):
        if request.META['HTTP_USER_AGENT'].lower().find('mobile') > 0:
            self.template_name = 'mobile/package.html'
        return super(PackageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Merge global settings to current context
        """
        context = super(PackageView, self).get_context_data(**kwargs)
        context['settings'] = preferences.Setting
        context['section_list'] = Section.objects.all().order_by('name')[:16]
        context['site'] = Site.objects.get(id=1)
        return context
