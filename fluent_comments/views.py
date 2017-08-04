from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.utils.html import escape
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from fluent_comments.utils import get_comment_template_name, get_comment_context_data

from .compat import get_form as get_comments_form, get_django_model, signals, CommentPostBadRequest
from fluent_comments import appsettings
import json, urllib, hashlib
import sys

if sys.version_info[0] >= 3:
    long = int


@csrf_protect
@require_POST
def post_comment_ajax(request, using=None):
    """
    Post a comment, via an Ajax call.
    """
    if not request.is_ajax():
        return HttpResponseBadRequest("Expecting Ajax call")

    # This is copied from django_comments.
    # Basically that view does too much, and doesn't offer a hook to change the rendering.
    # The request object is not passed to next_redirect for example.
    #
    # This is a separate view to integrate both features. Previously this used django-ajaxcomments
    # which is unfortunately not thread-safe (it it changes the comment view per request).

    # Fill out some initial data fields from an authenticated user, if present
    data = request.POST.copy()
    if request.user.is_authenticated():
        if not data.get('name', ''):
            data["name"] = request.user.get_full_name() or request.user.username
        if not data.get('email', ''):
            data["email"] = request.user.email

    # Look up the object we're trying to comment about
    ctype = data.get("content_type")
    object_pk = data.get("object_pk")
    if ctype is None or object_pk is None:
        return CommentPostBadRequest("Missing content_type or object_pk field.")
    try:
        model = get_django_model(*ctype.split(".", 1))
        target = model._default_manager.using(using).get(pk=object_pk)
    except ValueError:
        return CommentPostBadRequest("Invalid object_pk value: {0}".format(escape(object_pk)))
    except (TypeError, LookupError):
        return CommentPostBadRequest("Invalid content_type value: {0}".format(escape(ctype)))
    except AttributeError:
        return CommentPostBadRequest("The given content-type {0} does not resolve to a valid model.".format(escape(ctype)))
    except ObjectDoesNotExist:
        return CommentPostBadRequest("No object matching content-type {0} and object PK {1} exists.".format(escape(ctype), escape(object_pk)))
    except (ValueError, ValidationError) as e:
        return CommentPostBadRequest("Attempting go get content-type {0!r} and object PK {1!r} exists raised {2}".format(escape(ctype), escape(object_pk), e.__class__.__name__))

    # Do we want to preview the comment?
    preview = "preview" in data

    # Construct the comment form
    form = get_comments_form()(target, data=data)

    # Check security information
    if form.security_errors():
        return CommentPostBadRequest("The comment form failed security verification: {0}".format(form.security_errors()))

    # If there are errors or if we requested a preview show the comment
    if preview:
        comment = form.get_comment_object() if not form.errors else None
        return _ajax_result(request, form, "preview", comment, object_id=object_pk)
    if form.errors:
        return _ajax_result(request, form, "post", object_id=object_pk)

    # Otherwise create the comment
    comment = form.get_comment_object()
    comment.ip_address = request.META.get("REMOTE_ADDR", None)
    if request.user.is_authenticated():
        comment.user = request.user

    # Signal that the comment is about to be saved
    responses = signals.comment_will_be_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    for (receiver, response) in responses:
        if response is False:
            return CommentPostBadRequest("comment_will_be_posted receiver {0} killed the comment".format(receiver.__name__))

    # Save the comment and signal that it was saved
    comment.save()
    signals.comment_was_posted.send(
        sender  = comment.__class__,
        comment = comment,
        request = request
    )

    return _ajax_result(request, form, "post", comment, object_id=object_pk)


def _ajax_result(request, form, action, comment=None, object_id=None):
    # Based on django-ajaxcomments, BSD licensed.
    # Copyright (c) 2009 Brandon Konkle and individual contributors.
    #
    # This code was extracted out of django-ajaxcomments because
    # django-ajaxcomments is not threadsafe, and it was refactored afterwards.

    success = True
    json_errors = {}

    if form.errors:
        for field_name in form.errors:
            field = form[field_name]
            json_errors[field_name] = _render_errors(field)
        success = False

    json_return = {
        'success': success,
        'action': action,
        'errors': json_errors,
        'object_id': object_id,
        'use_threadedcomments': bool(appsettings.USE_THREADEDCOMMENTS),
    }

    if comment is not None:
        # Render the comment, like {% render_comment comment %} does
        context = get_comment_context_data(comment, action)
        template_name = get_comment_template_name(comment)
        comment_html = render_to_string(template_name, context)

        json_return.update({
            'html': comment_html,
            'comment_id': comment.id,
            'parent_id': None,
            'is_moderated': not comment.is_public,   # is_public flags changes in comment_will_be_posted
        })
        if appsettings.USE_THREADEDCOMMENTS:
            json_return['parent_id'] = comment.parent_id

    json_response = json.dumps(json_return)

    return HttpResponse(json_response, content_type="application/json")


def _render_errors(field):
    """
    Render form errors in crispy-forms style.
    """
    template = '{0}/layout/field_errors.html'.format(appsettings.CRISPY_TEMPLATE_PACK)
    return render_to_string(template, {
        'field': field,
        'form_show_errors': True,
    })


