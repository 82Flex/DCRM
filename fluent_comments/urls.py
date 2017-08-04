from .compat import urls as base_comments_urls
from . import views

try:
    # Django 1.6 requires this
    from django.conf.urls import url, include
except ImportError:
    # Django 1.3 compatibility, kept in minor release
    from django.conf.urls.defaults import url, include


urlpatterns = [
    url(r'^post/ajax/$', views.post_comment_ajax, name='comments-post-comment-ajax'),
    url(r'', include(base_comments_urls)),  # django_comments.urls or django.contrib.comments.urls
]
