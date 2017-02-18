# coding:utf-8

from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.actions import delete_selected


class OSVersionAdmin(admin.ModelAdmin):
    actions = [delete_selected]
    list_display = ('descriptor', 'build', 'created_at')
    search_fields = ['descriptor', 'build']
    readonly_fields = ['created_at']
    fieldsets = [
        ('General', {
            'fields': ['enabled', 'descriptor', 'build']
        }),
        ('Appearance', {
            'fields': ['icon']
        }),
        ('History', {
            'fields': ['created_at']
        }),
    ]
