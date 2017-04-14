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
from django.http import HttpResponseNotFound
from django.views.generic import DetailView
from django.views.decorators.clickjacking import xframe_options_exempt

from WEIPDCRM.models.version import Version

class PackageView(DetailView):
    model = Version
    context_object_name = 'package_info'
    pk_url_kwarg = 'package_id'
    template_name = 'frontend/package.html'

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        if request.META['HTTP_USER_AGENT'].lower().find('mobile') > 0:
            action_name = self.kwargs.get('action_name')
            if action_name == "contact":
                self.template_name = 'mobile/package/contact.html'
            elif action_name == "history":
                self.template_name = 'mobile/package/history.html'
            elif action_name is None:
                self.template_name = 'mobile/package/package.html'
            else:
                return HttpResponseNotFound()

        return super(PackageView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        package_id = self.kwargs.get('package_id')
        queryset = super(PackageView, self).get_queryset().filter(id=package_id, enabled=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PackageView, self).get_context_data(**kwargs)
        package_id = self.kwargs.get('package_id')
        action_name = self.kwargs.get('action_name')
        if action_name == "history":
            version = Version.objects.get(id=package_id)
            version_list = Version.objects.filter(c_package=version.c_package, enabled=True).order_by("-created_at")
            context["version_list"] = version_list
        return context
