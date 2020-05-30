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
import os, collections, shutil, json
from os.path import join, getsize

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.db import connection
from django.db.models import Sum
from preferences import preferences

from DCRM.settings import MEDIA_ROOT, TEMP_ROOT

from WEIPDCRM.models.version import Version
from WEIPDCRM.models.section import Section


def db_status():
    cursor = connection.cursor()
    status = collections.OrderedDict()
    query = ['Uptime', 'Queries', 'Threads_running', 'Slow_queries', 'Flush_commands', 'Open_tables']

    for key in query:
        sql = "SHOW STATUS LIKE '%s'" % key
        cursor.execute(sql)
        for (Variable_name, Value) in cursor:
            status[Variable_name] = int(Value)
    try:
        status['QPS'] = round(status['Queries'] / status['Uptime'], 2)
    except:
        status['QPS'] = 0

    return status


def statistics():
    stat = collections.OrderedDict()
    # Get download pool size
    version_path = os.path.join(MEDIA_ROOT, 'versions')
    download_pool_size = getdirsize(version_path)

    stat[_('Number of packages')] = Version.objects.count()
    stat[_('Number of enabled packages')] = Version.objects.filter(enabled=1).count()
    stat[_('Number of sections')] = Section.objects.count()
    stat[_('Total download times')] = Version.objects.aggregate(Sum('download_times'))['download_times__sum']
    stat[_('Temporarily files')] = nicesize(getdirsize(TEMP_ROOT)) + ' <a href="javascript:;" onclick="clean_all()">' + _(
        'Clean') + "</a>"
    stat[_('Downloadable files')] = nicesize(download_pool_size)
    stat[_('Total resources')] = nicesize(getdirsize(MEDIA_ROOT))
    return stat


def getdirsize(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        size += sum([getsize(join(root, name)) for name in files])
    return size


def nicesize(size):
    """
    Convert the given byteCount into a string like: 233 bytes/KB/MB/GB
    """
    for (cutoff, label) in [(1024 * 1024 * 1024, "GB"), (1024 * 1024, "MB"), (1024, "KB")]:
        if size >= cutoff:
            return "%.1f %s" % (size * 1.0 / cutoff, label)
    if size == 1:
        return "1 byte"
    else:
        bytes = "%.1f" % (size or 0,)
        return (bytes[:-2] if bytes.endswith('.0') else bytes) + ' bytes'


@staff_member_required
def statistics_view(request):
    """
    :param request: Django Request
    :return: Django HttpResponse
    :rtype: HttpResponse
    """
    if request.method == 'GET':
        context = admin.site.each_context(request)
        context.update({
            'title': _('Statistics'),
            'db_status': db_status(),
            'stat': statistics(),
            'settings': preferences.Setting,
        })

        template = 'admin/help/statistics.html'
        return render(request, template, context)
    else:
        if 'action' in request.POST and request.POST['action'] == 'clean_all':
            result_dict = {}
            try:
                # cache clear
                cache.clear()
                # remove all temporarily files
                if os.path.exists(TEMP_ROOT):
                    shutil.rmtree(TEMP_ROOT)
                    os.mkdir(TEMP_ROOT)
                else:
                    os.mkdir(TEMP_ROOT)
                result_dict = {"status": True}
                return HttpResponse(json.dumps(result_dict), content_type='application/json')
            except Exception as e:
                # error handler
                result_dict.update({
                    "success": False,
                    "exception": str(e)
                })
                return HttpResponse(json.dumps(result_dict), content_type='application/json')
