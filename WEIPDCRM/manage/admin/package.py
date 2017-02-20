# coding=utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.utils.safestring import mark_safe

from WEIPDCRM.models.version import Version


class PackageAdmin(admin.ModelAdmin):
    def package_(self, instance):
        """
        :type instance: Version
        """
        if instance.package is None:
            return "-"
        return mark_safe('<a href="' +
                         instance.get_change_list_url() + '?package__exact=' +
                         instance.package + '" target="_blank">' +
                         instance.package + '</a>')
    
    def version_(self, instance):
        """
        :type instance: Version
        """
        if instance.version is None:
            return "-"
        return mark_safe('<a href="' + instance.get_admin_url() + '" target="_blank">' +
                         instance.version + '</a>')
    
    list_display = (
        "package_",
        "version_",
        "name",
        "created_at"
    )
    list_display_links = ()
    search_fields = ['package', 'version', 'name']
    actions = []
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    change_list_template = 'admin/version_change_list.html'
