from datetime import date

from django import template
from django.utils.translation import gettext_lazy as _

from src.posts.models.post_model import Post

register = template.Library()


@register.inclusion_tag("posts/parts/archive.html")
def show_archive(**kwargs) -> dict:
    """
    substitute template sidebar `calender` with dropdown archive;
    data sorted by month(desc)
    """
    arch = Post.objects.get_public().datetimes("published_at", "month", order="DESC")
    archives = {}
    for item in arch:
        year = item.year
        month = item.month
        for i in range(1, 13):
            if i == month:
                try:
                    archives[year].append(
                        (
                            date(year, month, 1),
                            Post.objects.get_public()
                            .filter(published_at__month=month, published_at__year=year)
                            .count(),
                        )
                    )
                except KeyError:
                    archives[year] = [
                        (
                            date(year, month, 1),
                            Post.objects.get_public()
                            .filter(published_at__month=month, published_at__year=year)
                            .count(),
                        )
                    ]
    sorted_final = sorted(archives.items(), reverse=True)

    return {"archives": sorted_final}
