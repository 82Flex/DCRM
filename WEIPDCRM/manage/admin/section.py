# coding:utf-8

from django.contrib import admin
from django.utils.translation import ugettext as _

from WEIPDCRM.models.section import Section
from WEIPDCRM.models.package import Package


class SectionAdmin(admin.ModelAdmin):
    def generate_icon_package(self, request, queryset):
        self.message_user(request, _("Icon package generating job has been added to the \"default\" queue."))
    generate_icon_package.short_description = _("Generate icon package for selected sections")
    
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
    actions = [generate_icon_package]

    def get_readonly_fields(self, request, obj=None):
        """
        :type obj: Section
        """
        if Package.objects.filter(section=obj).count() > 0:
            return ['created_at', 'name']
        else:
            return ['created_at']
