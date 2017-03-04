# coding=utf-8

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

Notice: You have used class-based views, that's awesome.
        If not necessary, you can try function-based views.
        You may add lines above as license.
"""

from django.views.generic import ListView
from WEIPDCRM.models.version import Version

from preferences import preferences

class ChartView(ListView):
    model = Version
    context_object_name = 'package_list'
    ordering = '-download_times'
    template_name = 'frontend/chart.html'

    def get_queryset(self):
        """
        Get 12 packages ordering by download times.

        :return: QuerySet
        """

        queryset = super(ChartView, self).get_queryset().all()[:12]
        return queryset

    def get_context_data(self, **kwargs):
        """
        Merge global settings to current context
        """
        context = super(ChartView, self).get_context_data(**kwargs)
        context['settings'] = preferences.Setting
        return context