"""config URL Configuration 4.1"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from sandbox.sitemaps import PostSitemap

from src.core.utils.views_help import clear, terms
from src.core.views import home

sitemaps = {"posts": PostSitemap()}

urlpatterns = [
    path(
        "i18n/",
        include("django.conf.urls.i18n"),
    ),
    path("admin/", admin.site.urls),
    path("contacts/", include("src.contacts.urls")),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("terms", terms, name="terms"),
    path("in-development/", include("src.devs.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

htmx_urlpatterns = [
    path("clear", clear, name="clear"),
]

urlpatterns += i18n_patterns(
    path("", home, name="home"),
    path("general-info/", include("src.core.urls")),
    path("accounts/", include("allauth.urls")),
    path("profile/", include("src.profiles.urls")),
    path("posts/", include("src.posts.urls")),
    path("comments/", include("src.comments.urls")),
    path("notifications/", include("src.notifications.urls")),
)
urlpatterns += htmx_urlpatterns

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [path("rosetta/", include("rosetta.urls"))]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
