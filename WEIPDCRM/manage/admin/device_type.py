# coding:utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.actions import delete_selected


class DeviceTypeAdmin(admin.ModelAdmin):
    actions = [delete_selected]
    list_display = ('descriptor', 'subtype', 'platform', 'created_at')
    search_fields = ['descriptor', 'subtype', 'platform']
    readonly_fields = ['created_at']
    fieldsets = [
        ('General', {
            'fields': ['enabled', 'descriptor', 'subtype', 'platform']
        }),
        ('Appearance', {
            'fields': ['icon']
        }),
        ('History', {
            'fields': ['created_at']
        }),
    ]
    change_form_template = "admin/device_type/change_form.html"
