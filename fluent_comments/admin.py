import sys
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text
from django.utils.html import escape
from django.utils.translation import ugettext_lazy as _
from fluent_comments import appsettings
from .compat import get_model as get_comments_model, BASE_APP


# Ensure the admin app is loaded,
# so the model is unregistered here, and not loaded twice.
if appsettings.USE_THREADEDCOMMENTS:
    # Avoid getting weird situations where both comment apps are loaded in the admin.
    if not hasattr(settings, 'COMMENTS_APP') or settings.COMMENTS_APP == 'comments':
        raise ImproperlyConfigured("To use 'threadedcomments', specify the COMMENTS_APP as well")

    from threadedcomments.admin import ThreadedCommentsAdmin as CommentsAdminBase
else:
    # This code is not in the .compat module to avoid admin imports in all other code.
    # The admin import usually starts a model registration too, hence keep these imports here.
    if BASE_APP == 'django.contrib.comments':
        # Django 1.7 and below
        from django.contrib.comments.admin import CommentsAdmin as CommentsAdminBase
    elif BASE_APP == 'django_comments':
        # Django 1.8 and up
        from django_comments.admin import CommentsAdmin as CommentsAdminBase
    else:
        raise NotImplementedError()


class FluentCommentsAdmin(CommentsAdminBase):
    """
    Updated admin screen for the comments model.

    The ability to add a comment is removed here, the admin screen can only be used for managing comments.
    Adding comments can happen at the frontend instead.

    The fieldsets are more logically organized, and the generic relation is a readonly field instead of a massive pulldown + textarea.
    The class supports both the standard ``django_comments`` and the ``threadedcomments`` applications.
    """

    fieldsets = [
        (_('Content'),
           {'fields': ('object_link', 'user_name', 'user_email', 'user_url', 'comment', 'submit_date',)}
        ),
        (_('Account information'),
           {'fields': ('user', 'ip_address',)},
        ),
        (_('Moderation'),
           {'fields': ('is_public', 'is_removed')}
        ),
    ]

    list_display = ('user_name_col', 'object_link', 'ip_address', 'submit_date', 'is_public', 'is_removed')
    readonly_fields = ('object_link', 'user', 'ip_address', 'submit_date',)

    # Adjust the fieldsets for threaded comments
    if appsettings.USE_THREADEDCOMMENTS:
        fieldsets[0][1]['fields'] = ('object_link', 'user_name', 'user_email', 'user_url', 'title', 'comment', 'submit_date',)  # add title field.
        fieldsets.insert(2, (_('Hierarchy'), {'fields': ('parent',)}))
        raw_id_fields = ('parent',)

    def get_queryset(self, request):
        return super(FluentCommentsAdmin, self).get_queryset(request).select_related('user')

    def object_link(self, comment):
        try:
            object = comment.content_object
        except AttributeError:
            return ''

        if not object:
            return ''

        title = force_text(object)
        if hasattr(object, 'get_absolute_url'):
            return u'<a href="{0}">{1}</a>'.format(escape(object.get_absolute_url()), escape(title))
        else:
            return title

    object_link.short_description = _("Page")
    object_link.allow_tags = True

    def user_name_col(self, comment):
        if comment.user_name:
            return comment.user_name
        elif comment.user_id:
            # Can't do much else here, User model might be custom.
            if sys.version_info[0] >= 3:
                return str(comment.user)
            else:
                return unicode(comment.user)
        else:
            return None

    user_name_col.short_description = _("user's name")

    def has_add_permission(self, request):
        return False

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'title':
            kwargs['widget'] = AdminTextInputWidget
        return super(FluentCommentsAdmin, self).formfield_for_dbfield(db_field, **kwargs)


# Replace the old admin screen.
if appsettings.FLUENT_COMMENTS_REPLACE_ADMIN:
    CommentModel = get_comments_model()
    try:
        admin.site.unregister(CommentModel)
    except admin.sites.NotRegistered as e:
        pass

    admin.site.register(CommentModel, FluentCommentsAdmin)
