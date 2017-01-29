# coding:utf-8

from django.contrib import admin


class DeviceTypeAdmin(admin.ModelAdmin):
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