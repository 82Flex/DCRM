from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

AKISMET_API_KEY = getattr(settings, 'AKISMET_API_KEY', None)
AKISMET_BLOG_URL = getattr(settings, 'AKISMET_BLOG_URL', None)  # Optional, to override auto detection
AKISMET_IS_TEST = getattr(settings, 'AKISMET_IS_TEST', False)   # Enable in case of testing

CRISPY_TEMPLATE_PACK = getattr(settings, 'CRISPY_TEMPLATE_PACK', 'bootstrap')

USE_THREADEDCOMMENTS = 'threadedcomments' in settings.INSTALLED_APPS

FLUENT_COMMENTS_REPLACE_ADMIN = getattr(settings, "FLUENT_COMMENTS_REPLACE_ADMIN", True)

FLUENT_CONTENTS_USE_AKISMET = getattr(settings, 'FLUENT_CONTENTS_USE_AKISMET', bool(AKISMET_API_KEY))  # enable when an API key is set.
FLUENT_COMMENTS_USE_EMAIL_NOTIFICATION = getattr(settings, 'FLUENT_COMMENTS_USE_EMAIL_NOTIFICATION', True)  # enable by default
FLUENT_COMMENTS_CLOSE_AFTER_DAYS = getattr(settings, 'FLUENT_COMMENTS_CLOSE_AFTER_DAYS', None)
FLUENT_COMMENTS_MODERATE_BAD_WORDS = getattr(settings, 'FLUENT_COMMENTS_MODERATE_BAD_WORDS', ())
FLUENT_COMMENTS_MODERATE_AFTER_DAYS = getattr(settings, 'FLUENT_COMMENTS_MODERATE_AFTER_DAYS', None)
FLUENT_COMMENTS_AKISMET_ACTION = getattr(settings, 'FLUENT_COMMENTS_AKISMET_ACTION', 'soft_delete')  # or 'moderate', 'delete, 'soft_delete'

FLUENT_COMMENTS_FIELD_ORDER = tuple(getattr(settings, 'FLUENT_COMMENTS_FIELD_ORDER', ()) or ())
FLUENT_COMMENTS_EXCLUDE_FIELDS = getattr(settings, 'FLUENT_COMMENTS_EXCLUDE_FIELDS', ()) or ()
FLUENT_COMMENTS_FORM_CLASS = getattr(settings, 'FLUENT_COMMENTS_FORM_CLASS', None)
FLUENT_COMMENTS_FORM_CSS_CLASS = getattr(settings, 'FLUENT_COMMENTS_FORM_CSS_CLASS', 'comments-form form-horizontal')
FLUENT_COMMENTS_LABEL_CSS_CLASS = getattr(settings, 'FLUENT_COMMENTS_LABEL_CSS_CLASS', 'col-sm-2')
FLUENT_COMMENTS_FIELD_CSS_CLASS = getattr(settings, 'FLUENT_COMMENTS_FIELD_CSS_CLASS', 'col-sm-10')

# Compact style settings
FLUENT_COMMENTS_COMPACT_FIELDS = getattr(settings, 'FLUENT_COMMENTS_COMPACT_FIELDS', ('name', 'email', 'url'))
FLUENT_COMMENTS_COMPACT_GRID_SIZE = getattr(settings, 'FLUENT_COMMENTS_COMPACT_GRID_SIZE', 12)
FLUENT_COMMENTS_COMPACT_COLUMN_CSS_CLASS = getattr(settings, 'FLUENT_COMMENTS_COMPACT_COLUMN_CSS_CLASS', "col-sm-{size}")


if FLUENT_COMMENTS_AKISMET_ACTION not in ('moderate', 'soft_delete', 'delete'):
    raise ImproperlyConfigured("FLUENT_COMMENTS_AKISMET_ACTION can be 'moderate', 'soft_delete' or 'delete'")

if FLUENT_COMMENTS_EXCLUDE_FIELDS or FLUENT_COMMENTS_FORM_CLASS or FLUENT_COMMENTS_FIELD_ORDER:
    # The exclude option only works when our form is used.
    # Allow derived packages to inherit our form class too.
    if not hasattr(settings, 'COMMENTS_APP') or settings.COMMENTS_APP == 'comments':
        raise ImproperlyConfigured("To use django-fluent-comments, also specify: COMMENTS_APP = 'fluent_comments'")
