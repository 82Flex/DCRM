from fluent_comments.forms.base import AbstractCommentForm, CommentFormHelper


class DefaultCommentForm(AbstractCommentForm):
    """
    A simple contact form, backed by a model to save all data (in case email fails).
    """
    helper = CommentFormHelper()
