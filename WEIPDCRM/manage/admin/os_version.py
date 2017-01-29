# coding:utf-8

from django.contrib import admin


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
