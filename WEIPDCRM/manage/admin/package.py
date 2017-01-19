# coding:utf-8

from django.contrib import admin
from django.forms import ModelForm
from suit import apps
from suit.widgets import AutosizedTextarea


class PackageForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea,
        }


class PackageAdmin(admin.ModelAdmin):
    form = PackageForm
    list_display = ('enabled', 'package', 'name', 'section', 'author_name', 'created_at')
    search_fields = ['package', 'name', 'section', 'author_name']
    list_filter = ('enabled', 'section', )
    readonly_fields = ["created_at"]
    fieldsets = [
        ('General', {
            'fields': ['enabled', 'package', 'name', 'section', 'description']
        }),
        ('Contact', {
            'fields': ['author_name', 'author_email',
                       'maintainer_name', 'maintainer_email',
                       'sponsor_name', 'sponsor_email',
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

    def has_add_permission(self, request):
        return False
