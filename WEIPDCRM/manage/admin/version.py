# coding:utf-8

import json
from django.contrib import admin
from django.forms import ModelForm
# from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
# from django.core.urlresolvers import reverse

from django_rq import job, queues
from django.contrib import messages
from django.utils.translation import ugettext as _

from suit import apps
from suit.widgets import AutosizedTextarea

from WEIPDCRM.models.version import Version


class VersionForm(ModelForm):
    class Meta:
        widgets = {
            'update_logs': AutosizedTextarea
        }


@job("high")
def hash_update_job(queryset):
    for e in queryset:
        e.update_hash()
        e.save()
    return {"success": True}


@job("high")
def update_package_storage(package_id):
    obj = Version.objects.get(id=package_id)
    obj.update_storage()
    return {"success": True}


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

    def package_(self, instance):
        """
        :type instance: Version
        """
        return mark_safe('<a href="' + instance.package.get_admin_url() + '" target="_blank">' + str(instance.package) + '</a>')

    def storage_(self, instance):
        """
        :type instance: Version
        """
        return mark_safe('<a href="' + instance.storage_link + '" target="_blank">' + instance.storage_link + '</a>')

    form = VersionForm
    filter_horizontal = ('os_compatibility', 'device_compatibility')
    list_display = ('enabled', 'version', 'package', 'download_times', 'created_at')
    list_filter = ('enabled', )
    list_select_related = ('package',)
    list_display_links =('version', )
    # list_editable = ('enabled', )
    search_fields = ['version']
    readonly_fields = ['package_', 'storage_', 'download_times', 'md5',
                       'sha1', 'sha256', 'sha512', 'size', 'created_at',
                       'control_content']
    actions = [make_enabled, make_disabled, batch_hash_update]
    fieldsets = [
        ('General', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['enabled', 'package_', 'version', 'update_logs']
        }),
        ('File System', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['storage_', 'md5', 'sha1', 'sha256', 'sha512', 'size', 'download_times']
        }),
        ('Cydia', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['os_compatibility', 'device_compatibility']
        }),
        ('History', {
            'classes': ('suit-tab suit-tab-common',),
            'fields': ['created_at']
        }),
        ('Control Field', {
            'classes': ('suit-tab suit-tab-advanced',),
            'fields': ['control_content']
        }),
    ]
    suit_form_size = {
        'widgets': {
            'AutosizedTextarea': apps.SUIT_FORM_SIZE_X_LARGE,
        },
    }
    suit_form_tabs = (
        ('common', 'Common'),
        ('advanced', 'Advanced'),
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
        if change is True:
            if 'version' in form.changed_data:
                control = json.loads(obj.control_field)
                control.update({"Version": form.cleaned_data['version']})
                obj.control_field = json.dumps(control, sort_keys=True, indent=2)
            if ('version' in form.changed_data and obj.enabled) or ('enabled' in form.changed_data and form.cleaned_data['enabled']):
                update_package_storage.delay(obj.id)
                messages.info(request, _("%s storage updating job has been added to the \"high\" queue.") % str(obj))
        else:
            pass
        # hash update
        obj.update_hash()
        super(VersionAdmin, self).save_model(request, obj, form, change)

    change_list_template = 'admin/version_change_list.html'
