# coding=utf-8

from django import template
from django.contrib.admin.templatetags.admin_modify import submit_row as django_submit_row
register = template.Library()


@register.inclusion_tag('admin/release/change_action.html', takes_context=True)
def submit_row(context):
    """
    Currently only way of overriding Django admin submit_line.html is by replacing
    submit_row template tag in change_form.html
    """
    return django_submit_row(context)
