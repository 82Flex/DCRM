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

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.safestring import mark_safe

from WEIPDCRM.models.package import Package
from WEIPDCRM.models.version import Version


class PackageAdmin(admin.ModelAdmin):
    def package_(self, instance):
        """
        :type instance: Package
        """
        if instance.c_package is None:
            return "-"
        return mark_safe('<a href="' +
                         Version.get_change_list_url() + '?c_package__exact=' +
                         instance.c_package + '" target="_blank">' +
                         instance.c_package + '</a>')
    
    def version_(self, instance):
        """
        :type instance: Package
        """
        if instance.c_version is None:
            return "-"
        return mark_safe('<a href="' + instance.get_version_admin_url() + '" target="_blank">' +
                         instance.c_version + '</a>')
    
    list_display = (
        "package_",
        "version_",
        "c_name",
        "created_at"
    )
    list_display_links = None
    search_fields = ['c_package', 'c_version', 'c_name']
    actions = []
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    change_list_template = 'admin/version/change_list.html'
