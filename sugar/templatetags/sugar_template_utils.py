from django import template

register = template.Library()

class RenderInlineNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        source = self.nodelist.render(context)
        t = template.Template(source)
        return t.render(context)

@register.tag
def render_inline(parser, token):
    """
    Renders its contents to a string using the current context, allowing you
    to process template variables embedded in things like model content,
    django-flatblocks, etc.

    Usage:

    {%% render_inline %%}
    Foo

    Bar

    {{ something_with_embedded_django_template }}

    Baaz

    {%% end_render_inline %%}

    """

    nodelist = parser.parse(('end_render_inline',))

    parser.delete_first_token()

    return RenderInlineNode(nodelist)

class ContextManipulator(template.Node):
    """Add variables to the current template context

    Example:
        {%% set_context foo="bar" baaz=quux %%}
        {{ foo }} <- this will display "bar"
        {{ baaz }} <- the same as {{ quux }}

    """

    def __init__(self, *args):
        self.args = args

    def render(self, context):
        for arg in self.args:
            k, v = arg.split("=", 2)
            context[k] = template.Variable(v).resolve(context)

        return ""

    @classmethod
    def set_context_tag(cls, parser, token):
        try:
            bits = token.split_contents()
        except ValueError:
            raise template.TemplateSyntaxError(
                _('set_context_tag requires at least one arguments')
            )

        return ContextManipulator(bits[1], *bits[2:])

register.tag('set_context', ContextManipulator.set_context_tag)
