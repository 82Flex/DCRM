# coding:utf-8

from django.contrib import admin
from django.forms import ModelForm
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from suit import apps
from suit.widgets import AutosizedTextarea


class PackageForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea,
        }


def make_enabled(modeladmin, request, queryset):
    """
    :param queryset: QuerySet
    :type modeladmin: PackageAdmin
    """
    queryset.update(enabled=True)
make_enabled.short_description = _("Mark selected packages as enabled")


def make_disabled(modeladmin, request, queryset):
    """
    :param queryset: QuerySet
    :type modeladmin: PackageAdmin
    """
    queryset.update(enabled=False)
make_disabled.short_description = _("Mark selected packages as disabled")


class PackageAdmin(admin.ModelAdmin):
    form = PackageForm
    list_display = ('enabled', 'package', 'name', 'section', 'architecture', 'created_at', )
    search_fields = ['package', 'name']
    list_filter = ('enabled', 'section', )
    list_display_links = ('package',)
    # list_editable = ('section',)
    readonly_fields = ["created_at"]
    actions = [make_enabled, make_disabled]
    fieldsets = [
        ('General', {
            'fields': ['enabled', 'releases', 'package', 'name', 'section', 'architecture', 'description']
        }),
        ('Contact', {
            'fields': ['author_name', 'author_email',
                       'maintainer_name', 'maintainer_email',
                       'sponsor_name', 'sponsor_site',
                       'homepage']
        }),
        ('Appearance', {
            'fields': ['icon', 'depiction']
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

    # def has_add_permission(self, request):
    #     return False
    
    def save_model(self, request, obj, form, change):
        """
        :param change: Boolean
        :param form: PackageForm
        :type obj: Package
        """
        if change:
            pass
        super(PackageAdmin, self).save_model(request, obj, form, change)
