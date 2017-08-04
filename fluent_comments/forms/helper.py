from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Submit
from crispy_forms.utils import TEMPLATE_PACK
from django import forms
from django.forms.widgets import Input
from django.utils.translation import ugettext_lazy as _
from django_comments import get_form_target

from fluent_comments import appsettings


class CommentFormHelper(FormHelper):
    """
    The django-crispy-forms configuration that handles form appearance.
    The default is configured to show bootstrap forms nicely.
    """
    form_tag = False  # we need to define the form_tag
    form_id = 'comment-form-ID'
    form_class = 'js-comments-form {0}'.format(appsettings.FLUENT_COMMENTS_FORM_CSS_CLASS)
    label_class = appsettings.FLUENT_COMMENTS_LABEL_CSS_CLASS
    field_class = appsettings.FLUENT_COMMENTS_FIELD_CSS_CLASS
    render_unmentioned_fields = True  # like honeypot and security_hash

    BASE_FIELDS_TOP = ('content_type', 'object_pk', 'timestamp', 'security_hash')
    BASE_FIELDS_END = ('honeypot',)
    BASE_FIELDS = BASE_FIELDS_TOP + BASE_FIELDS_END

    if appsettings.USE_THREADEDCOMMENTS:
        BASE_FIELDS_TOP += ('parent',)

    @property
    def form_action(self):
        return get_form_target()  # reads get_form_target from COMMENTS_APP

    def __init__(self, form=None):
        super(CommentFormHelper, self).__init__(form=form)
        if form is not None:
            # When using the helper like this, it could generate all fields.
            self.form_id = 'comment-form-{0}'.format(form.target_object.pk)
            self.attrs = {
                'data-object-id': form.target_object.pk,
            }


class CompactLabelsCommentFormHelper(CommentFormHelper):
    """
    Compact labels in the form, show them as placeholder text instead.

    .. note::
        Make sure that the :attr:`layout` attribute is defined and
        it has fields added to it, otherwise the placeholders don't appear.

    The text input can easily be resized using CSS like:

    .. code-block: css

        @media only screen and (min-width: 768px) {
          form.comments-form input.form-control {
            width: 50%;
          }
        }

    """
    form_class = CommentFormHelper.form_class.replace('form-horizontal', 'form-vertical') + ' comments-form-compact'
    label_class = 'sr-only'
    field_class = ''

    def render_layout(self, form, context, template_pack=TEMPLATE_PACK):
        """
        Copy any field label to the ``placeholder`` attribute.
        Note, this method is called when :attr:`layout` is defined.
        """
        # Writing the label values into the field placeholders.
        # This is done at rendering time, so the Form.__init__() could update any labels before.
        # Django 1.11 no longer lets EmailInput or URLInput inherit from TextInput,
        # so checking for `Input` instead while excluding `HiddenInput`.
        for field in form.fields.values():
            if field.label and \
                    isinstance(field.widget, (Input, forms.Textarea)) and \
                    not isinstance(field.widget, forms.HiddenInput):
                field.widget.attrs['placeholder'] = u"{0}:".format(field.label)

        return super(CompactLabelsCommentFormHelper, self).render_layout(form, context, template_pack=template_pack)


class SubmitButton(Submit):
    """
    The submit button to add to the layout.

    Note: the ``name=post`` is mandatory, it helps the
    """

    def __init__(self, text=_("Submit"), **kwargs):
        super(SubmitButton, self).__init__(name='post', value=text, **kwargs)


class PreviewButton(Button):
    """
    The preview button to add to the layout.

    Note: the ``name=post`` is mandatory, it helps the
    """
    input_type = 'submit'

    def __init__(self, text=_("Preview"), **kwargs):
        kwargs.setdefault('css_class', 'btn-default')
        super(PreviewButton, self).__init__(name='preview', value=text, **kwargs)
