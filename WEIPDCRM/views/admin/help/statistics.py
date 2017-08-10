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
"""
from __future__ import division
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.utils.translation import ugettext as _

from django.db import connection, transaction

def db_status():
    cursor = connection.cursor()
    status = {}
    query = ['Queries','Uptime','Threads_running','Slow_queries','Flush_commands','Open_tables']

    for key in query:
        sql = ("SHOW STATUS LIKE '%s'") % key
        cursor.execute(sql)
        for (Variable_name, Value) in cursor:
            status[Variable_name] = int(Value)
    try:
        status['QPS'] = round(status['Queries']/status['Uptime'],2)
    except:
        status['QPS'] = 0

    return status

@staff_member_required
def statistics_view(request):
    """
    :param request: Django Request
    :return: Django HttpResponse
    :rtype: HttpResponse
    """
    context = admin.site.each_context(request)
    context.update({
        'title': _('Statistics'),
        'status': db_status()
    })

    template = 'admin/help/statistics.html'
    return render(request, template, context)
