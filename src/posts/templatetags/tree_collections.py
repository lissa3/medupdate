from django import template
from django.db.models import Count
from django.utils.html import format_html
from taggit.models import Tag

from src.core.utils.tree_help import get_cached_trees
from src.posts.models.categ_model import Category

register = template.Library()


class RecrTreeNode(template.Node):
    """for rendering nested categs"""

    def __init__(self, nodelist, queryset_var):
        self.nodelist = nodelist
        self.queryset_var = queryset_var

    def _render_node(self, context, node):
        """
        called in categ looping=> create recurs children
        Context (stack object) vs  RequestContex (req,{dict})
        can push() and pop() it;
        ReqCtx: takes settings ctx_proces vars met zich mee

        """
        bits = []
        context.push()
        for child in node.get_children():
            bits.append(self._render_node(context, child))
        context["node"] = node
        context["children"] = format_html("".join(bits))
        output = self.nodelist.render(context)
        context.pop()
        return output

    def render(self, context):
        # use the Variable class, instantiate it with
        # the name of the variable to be resolved,
        # and then call variable.resolve(context).
        qs = self.queryset_var.resolve(context)
        roots = get_cached_trees(qs)
        bits = [self._render_node(context, node) for node in roots]

        return "".join(bits)


@register.tag
def recursetree(parser, token):
    """
    Iterates over the nodes in the tree, and renders the
    contained block for each node. This tag will recursively
    render children into the template variable {{ children }}
    (mptt like )
    """
    bits = token.contents.split()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(("%s tag requires a queryset") % bits[0])

    queryset_var = template.Variable(bits[1])

    nodelist = parser.parse(("endrecursetree",))
    parser.delete_first_token()
    return RecrTreeNode(nodelist, queryset_var)


def calc_categ_posts(node) -> int:
    """recursive func to collect posts per categ node"""
    total = node.posts.filter(status=2).count()
    if node.get_children():
        for child in node.get_children():
            total += calc_categ_posts(child)
    return total


@register.inclusion_tag("components/categ_bar.html")
def show_categs() -> dict:
    categs = Category.get_root_nodes()
    for cat in categs:
        cat.num = calc_categ_posts(cat)
        cat.save()
    return {"categs": categs}


@register.inclusion_tag("components/comms/comments.html")
def show_comms(post, comments, user, **kwargs) -> dict:
    return {"comments": comments, "post": post, "user": user, **kwargs}


@register.inclusion_tag("components/tags.html")
def show_tags() -> dict:
    """substitute temp sidebar with tags for public posts"""
    tags = (
        Tag.objects.filter(post__status=2)
        .annotate(count=Count("post"))
        .filter(count__gt=0)
    )
    return {"tags": tags}
