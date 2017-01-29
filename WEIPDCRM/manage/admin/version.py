# coding:utf-8

from django.contrib import admin
from django.forms import ModelForm
# from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from django_rq import job, queues
# from django.contrib import messages
from django.utils.translation import ugettext as _
from suit import apps
from suit.widgets import AutosizedTextarea


class VersionForm(ModelForm):
    class Meta:
        widgets = {
            'update_logs': AutosizedTextarea
        }


@job("default")
def hash_update_job(queryset):
    for e in queryset:
        e.update_hash()
        e.save()
    return {"success": True}


class VersionAdmin(admin.ModelAdmin):
    def make_enabled(self, request, queryset):
        queryset.update(enabled=True)
    make_enabled.short_description = _("Mark selected versions as enabled")

    def make_disabled(self, request, queryset):
        queryset.update(enabled=False)
    make_disabled.short_description = _("Mark selected versions as disabled")

    def batch_hash_update(self, request, queryset):
        hash_update_job.delay(queryset)
        self.message_user(request, "Hash updating job has been added to the \"default\" queue.")
    batch_hash_update.short_description = _("Update hashes of selected versions")

    def package_(self, instance):
        return mark_safe('<a href="' + instance.package.get_admin_url() + '" target="_blank">' + str(instance.package) + '</a>')

    def storage_(self, instance):
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
        obj.update_hash()
        super(VersionAdmin, self).save_model(request, obj, form, change)
