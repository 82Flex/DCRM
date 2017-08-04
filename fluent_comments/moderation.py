import re
import fluent_comments
from akismet import Akismet
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str
from fluent_comments import appsettings
from .compat import BASE_APP

try:
    from django.contrib.sites.shortcuts import get_current_site  # Django 1.9+
except ImportError:
    from django.contrib.sites.models import get_current_site

if BASE_APP == 'django.contrib.comments':
    from django.contrib.comments.moderation import moderator, CommentModerator
elif BASE_APP == 'django_comments':
    from django_comments.moderation import moderator, CommentModerator
else:
    raise NotImplementedError()

try:
    from urllib.parse import urljoin  # Python 3
except ImportError:
    from urlparse import urljoin  # Python 2


RE_INTERPUNCTION = re.compile(r'\W+')

# Akismet code originally based on django-comments-spamfighter.

__all__ = (
    'FluentCommentsModerator',
    'moderate_model',
    'get_model_moderator',
    'comments_are_open',
    'comments_are_moderated',
)


class FluentCommentsModerator(CommentModerator):
    """
    Moderation policy for fluent-comments.
    """
    auto_close_field = None
    auto_moderate_field = None
    enable_field = None

    close_after = appsettings.FLUENT_COMMENTS_CLOSE_AFTER_DAYS
    moderate_after = appsettings.FLUENT_COMMENTS_MODERATE_AFTER_DAYS
    email_notification = False   # Using signals instead
    akismet_check = appsettings.FLUENT_CONTENTS_USE_AKISMET
    akismet_check_action = appsettings.FLUENT_COMMENTS_AKISMET_ACTION
    moderate_bad_words = set(appsettings.FLUENT_COMMENTS_MODERATE_BAD_WORDS)

    def allow(self, comment, content_object, request):
        """
        Determine whether a given comment is allowed to be posted on a given object.

        Returns ``True`` if the comment should be allowed, ``False`` otherwise.
        """
        # Parent class check
        if not super(FluentCommentsModerator, self).allow(comment, content_object, request):
            return False

        # Akismet check
        if self.akismet_check and self.akismet_check_action == 'delete':
            if self._akismet_check(comment, content_object, request):
                return False  # Akismet marked the comment as spam.

        return True

    def moderate(self, comment, content_object, request):
        """
        Determine whether a given comment on a given object should be allowed to show up immediately,
        or should be marked non-public and await approval.

        Returns ``True`` if the comment should be moderated (marked non-public), ``False`` otherwise.
        """

        # Soft delete checks are done first, so these comments are not mistakenly "just moderated"
        # for expiring the `close_after` date, but correctly get marked as spam instead.
        # This helps staff to quickly see which comments need real moderation.
        if self.akismet_check and self.akismet_check_action == 'soft_delete':
            if self._akismet_check(comment, content_object, request):
                comment.is_removed = True  # Set extra marker
                return True

        # Parent class check
        if super(FluentCommentsModerator, self).moderate(comment, content_object, request):
            return True

        # Bad words check
        if self.moderate_bad_words:
            input_words = set(RE_INTERPUNCTION.sub(' ', comment.comment).split())
            if self.moderate_bad_words.intersection(input_words):
                return True

        # Akismet check
        if self.akismet_check and self.akismet_check_action not in ('soft_delete', 'delete'):
            # Return True if akismet marks this comment as spam and we want to moderate it.
            if self._akismet_check(comment, content_object, request):
                return True

        return False

    def _akismet_check(self, comment, content_object, request):
        """
        Connects to Akismet and returns True if Akismet marks this comment as
        spam. Otherwise returns False.
        """
        # Get Akismet data
        AKISMET_API_KEY = appsettings.AKISMET_API_KEY
        if not AKISMET_API_KEY:
            raise ImproperlyConfigured('You must set AKISMET_API_KEY to use comment moderation with Akismet.')

        current_domain = get_current_site(request).domain
        auto_blog_url = '{0}://{1}/'.format(request.is_secure() and 'https' or 'http', current_domain)
        blog_url = appsettings.AKISMET_BLOG_URL or auto_blog_url

        akismet = Akismet(
            AKISMET_API_KEY,
            blog=blog_url,
            is_test=int(bool(appsettings.AKISMET_IS_TEST)),
            application_user_agent='django-fluent-comments/{0}'.format(fluent_comments.__version__),
        )

        akismet_data = self._get_akismet_data(blog_url, comment, content_object, request)
        return akismet.check(**akismet_data)  # raises AkismetServerError when key is invalid

    def _get_akismet_data(self, blog_url, comment, content_object, request):
        # Field documentation:
        # http://akismet.com/development/api/#comment-check
        data = {
            # Comment info
            'permalink': urljoin(blog_url, content_object.get_absolute_url()),
            'comment_type': 'comment',   # comment, trackback, pingback, see http://blog.akismet.com/2012/06/19/pro-tip-tell-us-your-comment_type/
            'comment_author': getattr(comment, 'name', ''),
            'comment_author_email': getattr(comment, 'email', ''),
            'comment_author_url': getattr(comment, 'url', ''),
            'comment_content': smart_str(comment.comment),
            'comment_date': comment.submit_date,

            # Request info
            'referrer': request.META.get('HTTP_REFERER', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'user_ip': comment.ip_address,
        }

        if comment.user_id and comment.user.is_superuser:
            data['user_role'] = 'administrator'  # always passes test

        # If the language is known, provide it.
        language = _get_article_language(content_object)
        if language:
            data['blog_lang'] = language

        return data


def moderate_model(ParentModel, publication_date_field=None, enable_comments_field=None):
    """
    Register a parent model (e.g. ``Blog`` or ``Article``) that should receive comment moderation.

    :param ParentModel: The parent model, e.g. a ``Blog`` or ``Article`` model.
    :param publication_date_field: The field name of a :class:`~django.db.models.DateTimeField` in the parent model which stores the publication date.
    :type publication_date_field: str
    :param enable_comments_field: The field name of a :class:`~django.db.models.BooleanField` in the parent model which stores the whether comments are enabled.
    :type enable_comments_field: str
    """
    attrs = {
        'auto_close_field': publication_date_field,
        'auto_moderate_field': publication_date_field,
        'enable_field': enable_comments_field,
    }
    ModerationClass = type(ParentModel.__name__ + 'Moderator', (FluentCommentsModerator,), attrs)
    moderator.register(ParentModel, ModerationClass)


def get_model_moderator(model):
    """
    Return the moderator class that is registered with a content object.
    If there is no associated moderator with a class, None is returned.

    :param model: The Django model registered with :func:`moderate_model`
    :type model: :class:`~django.db.models.Model`
    :return: The moderator class which holds the moderation policies.
    :rtype: :class:`~django_comments.moderation.CommentModerator`
    """
    try:
        return moderator._registry[model]
    except KeyError:
        return None


def comments_are_open(content_object):
    """
    Return whether comments are still open for a given target object.
    """
    moderator = get_model_moderator(content_object.__class__)
    if moderator is None:
        return True

    # Check the 'enable_field', 'auto_close_field' and 'close_after',
    # by reusing the basic Django policies.
    return CommentModerator.allow(moderator, None, content_object, None)


def comments_are_moderated(content_object):
    """
    Return whether comments are moderated for a given target object.
    """
    moderator = get_model_moderator(content_object.__class__)
    if moderator is None:
        return False

    # Check the 'auto_moderate_field', 'moderate_after',
    # by reusing the basic Django policies.
    return CommentModerator.moderate(moderator, None, content_object, None)


def _get_article_language(article):
    try:
        # django-parler uses this attribute
        return article.get_current_language()
    except AttributeError:
        pass

    try:
        return article.language_code
    except AttributeError:
        pass

    return None
