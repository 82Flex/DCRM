# coding:utf-8

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

import os

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.actions import delete_selected
from django.forms import ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from preferences import preferences
from suit import apps
from suit.widgets import AutosizedTextarea
from suit_redactor.widgets import RedactorWidget

from WEIPDCRM.models.version import Version

if settings.ENABLE_REDIS is True:
    import django_rq


class VersionForm(ModelForm):
    class Meta(object):
        widgets = {
            'rich_description': RedactorWidget,
            'update_logs': AutosizedTextarea,
            'c_description': AutosizedTextarea,
            'c_tag': AutosizedTextarea,
            'c_depends': AutosizedTextarea,
            'c_pre_depends': AutosizedTextarea,
            'c_conflicts': AutosizedTextarea,
            'c_replaces': AutosizedTextarea,
            'c_provides': AutosizedTextarea,
            'c_recommends': AutosizedTextarea,
            'c_suggests': AutosizedTextarea,
            'c_breaks': AutosizedTextarea,
            'c_installer_menu_item': AutosizedTextarea,
            'c_built_using': AutosizedTextarea,
            'c_built_for_profiles': AutosizedTextarea,
        }


def hash_update_job(queryset):
    """
    Batch hash updating job.
    """
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
        if settings.ENABLE_REDIS is True:
            queue = django_rq.get_queue('high')
            queue.enqueue(hash_update_job, queryset)
            self.message_user(request, _("Hash updating job has been added to the \"high\" queue."))
        else:
            hash_update_job(queryset)
            self.message_user(request, _("Hash updating job has been finished."))
    
    batch_hash_update.short_description = _("Update hashes of selected versions")
    
    def storage_(self, instance):
        """
        :type instance: Version
        """
        return mark_safe('<a href="' + instance.storage_link + '" target="_blank">' + instance.storage_link + '</a>')
    
    form = VersionForm
    actions = [make_enabled, make_disabled, batch_hash_update, delete_selected]
    filter_horizontal = (
        'os_compatibility',
        'device_compatibility'
    )
    list_display = (
        'enabled',
        'c_version',
        'c_package',
        'c_name',
        'c_section'
    )
    list_filter = ('enabled', 'c_section')
    list_display_links = ('c_version',)
    search_fields = ['c_version', 'c_package', 'c_name']
    readonly_fields = [
        'storage_',
        'download_times',
        'c_md5',
        'c_sha1',
        'c_sha256',
        'c_sha512',
        'c_size',
        'created_at'
    ]
    fieldsets = [
        # Common
        (_('Basic'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['enabled', 'c_package', 'c_version']
        }),
        (_('Display'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['c_name', 'c_section', 'gallery', 'c_icon', 'online_icon', 'c_description', 'update_logs']
        }),
        (_('Links'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['custom_depiction', 'c_depiction', 'c_homepage', 'rich_description']
        }),
        (_('Compatibility'), {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['os_compatibility', 'device_compatibility']
        }),
        # Contact
        (_('Maintainer'), {
            'classes': ('suit-tab suit-tab-contact',),
            'fields': ['maintainer_name', 'maintainer_email']
        }),
        (_('Author'), {
            'classes': ('suit-tab suit-tab-contact',),
            'fields': ['author_name', 'author_email']
        }),
        (_('Sponsor'), {
            'classes': ('suit-tab suit-tab-contact',),
            'fields': ['sponsor_name', 'sponsor_site']
        }),
        # Advanced
        (_('Platform'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['c_architecture', 'c_priority', 'c_essential', 'c_tag']
        }),
        (_('Relations'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['c_depends', 'c_pre_depends', 'c_conflicts', 'c_replaces', 'c_provides']
        }),
        (_('Other Relations'), {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['c_recommends', 'c_suggests', 'c_breaks']
        }),
        # File System
        (_('Storage'), {
            'classes': ('suit-tab suit-tab-file-system',),
            'fields': ['storage_', 'c_size', 'c_installed_size']
        }),
        (_('Hash'), {
            'classes': ('suit-tab suit-tab-file-system',),
            'fields': ['c_md5', 'c_sha1', 'c_sha256', 'c_sha512']
        }),
        # Others
        (_('Provider'), {
            'classes': ('suit-tab suit-tab-others',),
            'fields': ['c_origin', 'c_source', 'c_bugs', 'c_installer_menu_item']
        }),
        (_('Make'), {
            'classes': ('suit-tab suit-tab-others',),
            'fields': ['c_build_essential', 'c_built_using', 'c_built_for_profiles']
        }),
        (_('Development'), {
            'classes': ('suit-tab suit-tab-others',),
            'fields': ['c_multi_arch', 'c_subarchitecture', 'c_kernel_version']
        }),
        (_('History'), {
            'classes': ('suit-tab suit-tab-statistics',),
            'fields': ['created_at', 'download_times']
        })
    ]
    suit_form_size = {
        'widgets': {
            'RedactorWidget': apps.SUIT_FORM_SIZE_X_LARGE,
        }
    }
    suit_form_tabs = (
        ('common', _('Common')),
        ('contact', _('Contact')),
        ('advanced', _('Advanced')),
        ('file-system', _('File System')),
        ('others', _('Others')),
        ('statistics', _('Statistics'))
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
        
        """
        Remove all excluded column (which are not in standard debian control part)
        to determine whether the related .deb file on file system should be updated.
        """
        excluded_column = ['enabled', 'created_at', 'os_compatibility', 'device_compatibility',
                           'update_logs', 'storage', 'online_icon', 'gallery', 'c_md5', 'c_sha1', 'c_sha256', 'c_sha512',
                           'c_size', 'download_times', 'rich_description']
        change_list = form.changed_data
        change_num = len(change_list)
        for change_var in change_list:
            if change_var in excluded_column:
                change_num -= 1
        if change is True and change_num > 0:
            update_job = obj.update_storage()
            if settings.ENABLE_REDIS is True and update_job is not None:
                messages.info(request, mark_safe(_("The Version \"<a href=\"{job_detail}\">{obj}</a>\" storage updating job has been added to the \"<a href=\"{jobs}\">high</a>\" queue.").format(
                        job_detail=reverse('rq_job_detail', kwargs={
                            'queue_index': 1,
                            'job_id': update_job.id,
                        }),
                        obj=str(obj),
                        jobs=reverse('rq_jobs', args=(1, ))
                    )
                ))
        else:
            pass
    
    def delete_model(self, request, obj):
        """
        :type obj: Version
        """
        abs_path = os.path.join(settings.MEDIA_ROOT, obj.storage.name)
        os.unlink(abs_path)
        super(VersionAdmin, self).delete_model(request, obj)
    
    def get_list_display(self, request):
        if preferences.Setting.download_count:
            return (
                'enabled',
                'c_version',
                'c_package',
                'c_name',
                'c_section',
                'download_times'
            )
        else:
            return (
                'enabled',
                'c_version',
                'c_package',
                'c_name',
                'c_section'
            )

    change_list_template = 'admin/version/change_list.html'
    change_form_template = 'admin/version/change_form.html'

    # TODO: beautify django queue pages
