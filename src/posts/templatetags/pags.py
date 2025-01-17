from django import template

register = template.Library()


@register.inclusion_tag("components/htmx_pags.html")
def pags_htmx(tag=None, slug=None, page_obj=None, request=None, year=None, month=None):
    """htmx-pagination for tags/categ/calend search"""
    ctx = {"page_obj": page_obj, "req_url": request.path}
    if tag:
        ctx.update({"tag": tag})
    if slug:
        ctx.update({"slug": slug})
    if year and month:
        {ctx.update({"year": year, "month": month})}

    return ctx
