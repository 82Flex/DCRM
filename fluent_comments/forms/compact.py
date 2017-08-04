"""
Different form layout, very compact
"""
from crispy_forms.layout import Column, Layout, Row
from django.utils.functional import cached_property

from fluent_comments import appsettings
from fluent_comments.forms.base import AbstractCommentForm, PreviewButton, SubmitButton
from fluent_comments.forms.helper import CompactLabelsCommentFormHelper


class CompactLabelsCommentForm(AbstractCommentForm):
    """
    A form layout where the labels are replaced with ``placeholder`` attributes.
    """

    @cached_property
    def helper(self):
        # Initialize on demand
        helper = CompactLabelsCommentFormHelper()
        helper.layout = Layout(*self.fields.keys())
        helper.add_input(SubmitButton())
        helper.add_input(PreviewButton())
        return helper


class CompactCommentForm(AbstractCommentForm):
    """
    A form with a very compact layout;
    all the name/email/phone fields are displayed in a single top row.
    It uses Bootstrap 3 layout by default to generate the columns.
    """
    top_row_fields = appsettings.FLUENT_COMMENTS_COMPACT_FIELDS
    top_row_columns = appsettings.FLUENT_COMMENTS_COMPACT_GRID_SIZE
    top_column_class = appsettings.FLUENT_COMMENTS_COMPACT_COLUMN_CSS_CLASS

    @cached_property
    def helper(self):
        # As extra service, auto-adjust the layout based on the project settings.
        # This allows defining the top-row, and still get either 2 or 3 columns
        compact_fields = [name for name in self.fields.keys() if name in self.top_row_fields]
        other_fields = [name for name in self.fields.keys() if name not in self.top_row_fields]
        col_size = int(self.top_row_columns / len(compact_fields))
        col_class = self.top_column_class.format(size=col_size)

        compact_row = Row(*[Column(name, css_class=col_class) for name in compact_fields])

        # The fields are already ordered by the AbstractCommentForm.__init__ method.
        # See where the compact row should be.
        pos = list(self.fields.keys()).index(compact_fields[0])
        new_fields = other_fields
        new_fields.insert(pos, compact_row)

        helper = CompactLabelsCommentFormHelper()
        helper.layout = Layout(*new_fields)
        helper.add_input(SubmitButton())
        helper.add_input(PreviewButton())
        return helper
