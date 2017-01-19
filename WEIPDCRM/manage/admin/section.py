# coding:utf-8

from django.contrib import admin


class SectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ['name']
    readonly_fields = ['created_at']
    fieldsets = [
        ('General', {
            'fields': ['name']
        }),
        ('Appearance', {
            'fields': ['icon']
        }),
        ('History', {
            'fields': ['created_at']
        }),
    ]
