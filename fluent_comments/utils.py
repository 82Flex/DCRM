"""
Internal utils
"""
import sys
import traceback

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from fluent_comments import appsettings

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module  # Python 2.6 compatibility


def get_comment_template_name(comment):
    """
    Internal function for the rendering of comments.
    """
    ctype = ContentType.objects.get_for_id(comment.content_type_id)
    return [
        "comments/%s/%s/comment.html" % (ctype.app_label, ctype.model),
        "comments/%s/comment.html" % ctype.app_label,
        "comments/comment.html"
    ]


def get_comment_context_data(comment, action=None):
    """
    Internal function for the rendering of comments.
    """
    return {
        'comment': comment,
        'action': action,
        'preview': (action == 'preview'),
        'USE_THREADEDCOMMENTS': appsettings.USE_THREADEDCOMMENTS,
    }


def import_symbol(import_path, setting_name):
    """
    Import a class or function by name.
    """
    mod_name, class_name = import_path.rsplit('.', 1)

    # import module
    try:
        mod = import_module(mod_name)
        cls = getattr(mod, class_name)
    except ImportError as e:
        __, __, exc_traceback = sys.exc_info()
        frames = traceback.extract_tb(exc_traceback)
        if len(frames) > 1 and any('importlib' not in f[0] for f in frames[1:]):
            raise   # import error is a level deeper.

        raise ImproperlyConfigured("{0} does not point to an existing class: {1}".format(setting_name, import_path))
    except AttributeError:
        raise ImproperlyConfigured("{0} does not point to an existing class: {1}".format(setting_name, import_path))

    return cls

