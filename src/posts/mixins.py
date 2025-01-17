from django.urls import reverse
from django.utils.functional import cached_property


class PostListMenuMixin:
    @cached_property
    def crumbs(self):
        """build chached post crumbs"""
        return [{"name": "Home"}, {"name": "posts", "url": reverse("posts:post_list")}]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["crumbs"] = self.crumbs
        return ctx


class CategoryCrumbMixin:
    def get_post_categs_path(self) -> list:
        """
        list of dict's based on a given p.category:
        {key:p.category slug, value: p.category name}
        incl ancestors for UI: categs links
        """
        post = self.get_object()
        cats_names = post.categ.get_name_slug_chain()
        slugs_keys = cats_names["path_slug"].split("/")
        names_vals = cats_names["path_name"].split("/")
        if len(slugs_keys) == len(names_vals):
            res = dict(zip(slugs_keys, names_vals, strict=True))
        else:
            return []
        chain_crumbs = []
        for slug, name in res.items():
            chain_crumbs.append(
                {
                    "path": reverse("posts:cat_search", kwargs={"slug": slug}),
                    "name": name,
                }
            )
        return chain_crumbs
