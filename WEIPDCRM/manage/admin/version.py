# coding:utf-8

from django.contrib import admin
from django.forms import ModelForm
from suit import apps
from suit.widgets import AutosizedTextarea


class VersionForm(ModelForm):
    class Meta:
        widgets = {
            'update_logs': AutosizedTextarea,
        }


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


class OSVersionAdmin(admin.ModelAdmin):
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


class VersionAdmin(admin.ModelAdmin):
    form = VersionForm
    filter_horizontal = ('os_compatibility', 'device_compatibility')
    list_display = ('enabled', 'package', 'version', 'download_times', 'created_at')
    list_filter = ('enabled',)
    search_fields = ['package', 'version']
    readonly_fields = ['package', 'download_times', 'md5', 'sha1', 'sha256', 'size', 'created_at']
    fieldsets = [
        ('General', {
            'fields': ['enabled', 'package', 'version', 'update_logs']
        }),
        ('File System', {
            'fields': ['storage', 'md5', 'sha1', 'sha256', 'size', 'download_times']
        }),
        ('Compatibility', {
            'fields': ['os_compatibility', 'device_compatibility']
        }),
        ('History', {
            'fields': ['created_at']
        }),
    ]
    suit_form_size = {
        'widgets': {
            'AutosizedTextarea': apps.SUIT_FORM_SIZE_X_LARGE,
        },
    }

    def has_add_permission(self, request):
        return False
