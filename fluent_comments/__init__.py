"""
API for :ref:`custom-comment-app-api`
"""
form_class = None
model_class = None

# following PEP 440
__version__ = "1.4.2"


def get_model():
    """
    Return the model to use for commenting.
    """
    global model_class
    if model_class is None:
        from fluent_comments import appsettings
        if appsettings.USE_THREADEDCOMMENTS:
            from threadedcomments.models import ThreadedComment
            model_class = ThreadedComment
        else:
            # Our proxy model that performs select_related('user') for the comments
            from fluent_comments.models import FluentComment
            model_class = FluentComment

    return model_class


def get_form():
    """
    Return the form to use for commenting.
    """
    global form_class
    from fluent_comments import appsettings
    if form_class is None:
        if appsettings.FLUENT_COMMENTS_FORM_CLASS:
            from fluent_comments.utils import import_symbol
            form_class = import_symbol(appsettings.FLUENT_COMMENTS_FORM_CLASS, 'FLUENT_COMMENTS_FORM_CLASS')
        else:
            from fluent_comments.forms import FluentCommentForm
            form_class = FluentCommentForm

    return form_class
