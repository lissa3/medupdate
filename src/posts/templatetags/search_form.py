from django import template

from src.posts.forms import SearchForm

register = template.Library()


@register.inclusion_tag("components/search.html")
def show_search_form():
    search_form = SearchForm()
    return {"search_form": search_form}
