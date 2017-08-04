from django.core.exceptions import ImproperlyConfigured
from fluent_comments import appsettings
from fluent_comments.forms.helper import CommentFormHelper
from fluent_comments.forms.helper import SubmitButton, PreviewButton  # noqa, import at old class location too

try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict  # Python 2.6


if appsettings.USE_THREADEDCOMMENTS:
    from threadedcomments.forms import ThreadedCommentForm as base_class
else:
    from fluent_comments.compat import CommentForm as base_class


class AbstractCommentForm(base_class):
    """
    The comment form, applies various settings.
    """

    #: Helper for {% crispy %} template tag
    helper = CommentFormHelper()

    def __init__(self, *args, **kwargs):
        super(AbstractCommentForm, self).__init__(*args, **kwargs)

        # Remove fields from the form.
        # This has to be done in the constructor, because the ThreadedCommentForm
        # inserts the title field in the __init__, instead of the static form definition.
        for name in appsettings.FLUENT_COMMENTS_EXCLUDE_FIELDS:
            try:
                self.fields.pop(name)
            except KeyError:
                raise ImproperlyConfigured("Field name '{0}' in FLUENT_COMMENTS_EXCLUDE_FIELDS is invalid, it does not exist in the comment form.")

        if appsettings.FLUENT_COMMENTS_FIELD_ORDER:
            new_fields = OrderedDict()
            ordering = (
                CommentFormHelper.BASE_FIELDS_TOP +
                appsettings.FLUENT_COMMENTS_FIELD_ORDER +
                CommentFormHelper.BASE_FIELDS_END
            )
            for name in ordering:
                new_fields[name] = self.fields[name]
            self.fields = new_fields

    def get_comment_create_data(self, *args, **kwargs):
        # Fake form data for excluded fields, so there are no KeyError exceptions
        for name in appsettings.FLUENT_COMMENTS_EXCLUDE_FIELDS:
            self.cleaned_data[name] = ""

        # Pass args, kwargs for django-contrib-comments 1.8, which accepts a ``site_id`` argument.
        return super(AbstractCommentForm, self).get_comment_create_data(*args, **kwargs)
