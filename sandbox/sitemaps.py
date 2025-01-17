from django.contrib.sitemaps import Sitemap

from src.posts.models.post_model import Post


class PostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    i18n = True

    def items(self):
        return Post.objects.get_public()
