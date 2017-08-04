import django
from django.conf import settings
from django.template import Library, Node
from django.template.loader import get_template
from fluent_comments.utils import get_comment_template_name, get_comment_context_data
from tag_parser import parse_token_kwargs
from tag_parser.basetags import BaseInclusionNode
from fluent_comments import appsettings
from fluent_comments.models import get_comments_for_model
from fluent_comments.moderation import comments_are_open, comments_are_moderated
try:
    from django.template import context_processors  # Django 1.10+
except:
    from django.core import context_processors


register = Library()


class AjaxCommentTags(BaseInclusionNode):
    """
    Custom inclusion node with some special parsing features.
    Using the ``@register.inclusion_tag`` is not sufficient,
    because some keywords require custom parsing.
    """
    template_name = "fluent_comments/templatetags/ajax_comment_tags.html"
    min_args = 1
    max_args = 1

    @classmethod
    def parse(cls, parser, token):
        """
        Custom parsing for the ``{% ajax_comment_tags for ... %}`` tag.
        """
        # Process the template line.
        tag_name, args, kwargs = parse_token_kwargs(
            parser, token,
            allowed_kwargs=cls.allowed_kwargs,
            compile_args=False,  # Only overrule here, keep at render() phase.
            compile_kwargs=cls.compile_kwargs
        )

        # remove "for" keyword, so all other args can be resolved in render().
        if args[0] == 'for':
            args.pop(0)

        # And apply the compilation afterwards
        for i in range(len(args)):
            args[i] = parser.compile_filter(args[i])

        cls.validate_args(tag_name, *args, **kwargs)
        return cls(tag_name, *args, **kwargs)

    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        """
        The main logic for the inclusion node, analogous to ``@register.inclusion_node``.
        """
        target_object = tag_args[0]  # moved one spot due to .pop(0)
        new_context = {
            'STATIC_URL': parent_context.get('STATIC_URL', None),
            'USE_THREADEDCOMMENTS': appsettings.USE_THREADEDCOMMENTS,
            'target_object': target_object,
        }

        # Be configuration independent:
        if new_context['STATIC_URL'] is None:
            try:
                request = parent_context['request']
            except KeyError:
                new_context.update({'STATIC_URL': settings.STATIC_URL})
            else:
                new_context.update(context_processors.static(request))

        return new_context


@register.tag
def ajax_comment_tags(parser, token):
    """
    Display the required ``<div>`` elements to let the Ajax comment functionality work with your form.
    """
    return AjaxCommentTags.parse(parser, token)


register.filter('comments_are_open', comments_are_open)
register.filter('comments_are_moderated', comments_are_moderated)


@register.filter
def comments_count(content_object):
    """
    Return the number of comments posted at a target object.

    You can use this instead of the ``{% get_comment_count for [object] as [varname]  %}`` tag.
    """
    return get_comments_for_model(content_object).count()


class FluentCommentsList(Node):

    def render(self, context):
        # Include proper template, avoid parsing it twice by operating like @register.inclusion_tag()
        if not getattr(self, 'nodelist', None):
            if appsettings.USE_THREADEDCOMMENTS:
                template = get_template("fluent_comments/templatetags/threaded_list.html")
            else:
                template = get_template("fluent_comments/templatetags/flat_list.html")
            self.nodelist = template

        # NOTE NOTE NOTE
        # HACK: Determine the parent object based on the comment list queryset.
        # the {% render_comment_list for article %} tag does not pass the object in a general form to the template.
        # Not assuming that 'object.pk' holds the correct value.
        #
        # This obviously doesn't work when the list is empty.
        # To address that, the client-side code also fixes that, by looking for the object ID in the nearby form.
        target_object_id = context.get('target_object_id', None)
        if not target_object_id:
            comment_list = context['comment_list']
            if isinstance(comment_list, list) and comment_list:
                target_object_id = comment_list[0].object_pk

        # Render the node
        context['USE_THREADEDCOMMENTS'] = appsettings.USE_THREADEDCOMMENTS
        context['target_object_id'] = target_object_id

        if django.VERSION >= (1, 8):
            context = context.flatten()
        return self.nodelist.render(context)


@register.tag
def fluent_comments_list(parser, token):
    """
    A tag to select the proper template for the current comments app.
    """
    return FluentCommentsList()


class RenderCommentNode(BaseInclusionNode):
    min_args = 1
    max_args = 1

    def get_template_name(self, *tag_args, **tag_kwargs):
        return get_comment_template_name(comment=tag_args[0])

    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        return get_comment_context_data(comment=tag_args[0])


@register.tag
def render_comment(parser, token):
    """
    Render a single comment.
    This tag does not exist in the standard django_comments,
    because it only renders a complete list.
    """
    return RenderCommentNode.parse(parser, token)

