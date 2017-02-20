# coding:utf-8

from __future__ import unicode_literals

import os

from django.contrib import admin
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from django_rq import job
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.contrib.admin.actions import delete_selected

from suit import apps
from suit.widgets import AutosizedTextarea

from WEIPDCRM.models.version import Version


class VersionForm(ModelForm):
    class Meta(object):
        widgets = {
            'update_logs': AutosizedTextarea
        }


@job("high")
def hash_update_job(queryset):
    succeed = True
    for e in queryset:
        try:
            e.update_hash()
            e.save()
        except Exception as e:
            succeed = False
    return {"success": succeed}


class VersionAdmin(admin.ModelAdmin):
    def make_enabled(self, request, queryset):
        """
        :type queryset: QuerySet
        """
        queryset.update(enabled=True)
    make_enabled.short_description = _("Mark selected versions as enabled")

    def make_disabled(self, request, queryset):
        """
        :type queryset: QuerySet
        """
        queryset.update(enabled=False)
    make_disabled.short_description = _("Mark selected versions as disabled")

    def batch_hash_update(self, request, queryset):
        """
        :type queryset: QuerySet
        """
        hash_update_job.delay(queryset)
        self.message_user(request, _("Hash updating job has been added to the \"high\" queue."))
    batch_hash_update.short_description = _("Update hashes of selected versions")

    def storage_(self, instance):
        """
        :type instance: Version
        """
        return mark_safe('<a href="' + instance.storage_link + '" target="_blank">' + instance.storage_link + '</a>')
    
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
    
    def section_(self, instance):
        """
        :type instance: Version
        """
        if instance.section is None:
            return "-"
        return mark_safe('<a href="' +
                         instance.get_change_list_url() + '?section__id__exact=' +
                         unicode(instance.section.id) + '" target="_blank">' +
                         instance.section.name + '</a>')
    
    form = VersionForm
    actions = [make_enabled, make_disabled, batch_hash_update, delete_selected]
    filter_horizontal = (
        'os_compatibility',
        'device_compatibility'
    )
    list_display = (
        'enabled',
        'version',
        'package_',
        'name',
        'section_'
    )
    list_filter = ('enabled', 'section')
    list_display_links = ('version', )
    search_fields = ['version', 'package', 'name']
    readonly_fields = [
        'storage_',
        'download_times',
        'md5',
        'sha1',
        'sha256',
        'sha512',
        'size',
        'created_at'
    ]
    fieldsets = [
        # Common
        ('Basic', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['enabled', 'package', 'version']
        }),
        ('Display', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['name', 'section', 'icon', 'description', 'update_logs']
        }),
        ('Links', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['custom_depiction', 'depiction', 'homepage']
        }),
        ('Compatibility', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['os_compatibility', 'device_compatibility']
        }),
        # Contact
        ('Maintainer', {
            'classes': ('suit-tab suit-tab-contact',),
            'fields': ['maintainer_name', 'maintainer_email']
        }),
        ('Author', {
            'classes': ('suit-tab suit-tab-contact',),
            'fields': ['author_name', 'author_email']
        }),
        ('Sponsor', {
            'classes': ('suit-tab suit-tab-contact',),
            'fields': ['sponsor_name', 'sponsor_site']
        }),
        # Advanced
        ('Platform', {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['architecture', 'priority', 'essential', 'tag']
        }),
        ('Relations', {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['depends', 'pre_depends', 'conflicts', 'replaces', 'provides']
        }),
        ('Other Relations', {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['recommends', 'suggests', 'breaks']
        }),
        # File System
        ('Storage', {
            'classes': ('suit-tab suit-tab-file-system',),
            'fields': ['storage_', 'size', 'installed_size']
        }),
        ('Hash', {
            'classes': ('suit-tab suit-tab-file-system',),
            'fields': ['md5', 'sha1', 'sha256', 'sha512']
        }),
        # Others
        ('Provider', {
            'classes': ('suit-tab suit-tab-others',),
            'fields': ['origin', 'source', 'bugs', 'installer_menu_item']
        }),
        ('Make', {
            'classes': ('suit-tab suit-tab-others',),
            'fields': ['build_essential', 'built_using', 'built_for_profiles']
        }),
        ('Development', {
            'classes': ('suit-tab suit-tab-others',),
            'fields': ['multi_arch', 'subarchitecture', 'kernel_version']
        }),
        ('History', {
            'classes': ('suit-tab suit-tab-statistics',),
            'fields': ['created_at', 'download_times']
        }),
    ]
    suit_form_size = {
        'widgets': {
            'AutosizedTextarea': apps.SUIT_FORM_SIZE_X_LARGE,
        },
    }
    suit_form_tabs = (
        ('common', 'Common'),
        ('contact', 'Contact'),
        ('advanced', 'Advanced'),
        ('file-system', 'File System'),
        ('others', 'Others'),
        ('statistics', 'Statistics')
    )

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        # field update
        """
        :param change: Boolean
        :param form: VersionForm
        :type obj: Version
        """
        # hash update
        obj.update_hash()
        super(VersionAdmin, self).save_model(request, obj, form, change)
        excluded_column = ['enabled', 'created_at', 'os_compatibility', 'device_compatibility',
                           'update_logs', 'storage', 'icon', 'md5', 'sha1', 'sha256', 'sha512',
                           'size', 'download_times']
        change_list = form.changed_data
        change_num = len(change_list)
        for change_var in change_list:
            if change_var in excluded_column:
                change_num -= 1
        if change is True and change_num > 0:
            obj.update_storage()
            messages.info(request, _("%s storage updating job has been added to the \"high\" queue.") % str(obj))
        else:
            pass
    
    def delete_model(self, request, obj):
        """
        :type obj: Version
        """
        os.unlink(obj.storage.name)
        super(VersionAdmin, self).delete_model(request, obj)

    change_list_template = 'admin/version_change_list.html'
