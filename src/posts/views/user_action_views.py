from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin as LRM
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext_lazy as _
from django.views import View

from src.devs.mixins import RestrictHtmxMixin
from src.posts.models.post_model import Post
from src.posts.models.relation_model import Relation
from src.profiles.models import Profile

User = get_user_model()


class TrackLike(LRM, RestrictHtmxMixin, View):
    def post(self, request):
        """
        htmx based; create or toggle user likes;
        small html: check for total likes
        """
        post_uuid = request.POST.get("post_uuid", None)
        user_id = request.POST.get("user_id", None)
        post = get_object_or_404(Post, uuid=post_uuid)
        user = get_object_or_404(User, id=user_id)
        ctx = {}
        try:
            rel_obj = Relation.objects.select_related("user", "post").get(
                user=user, post=post
            )
            if rel_obj.like is None:
                rel_obj.like = True
            else:
                rel_obj.like = not bool(rel_obj.like)
            ctx.update({"liked": rel_obj.like})
            rel_obj.save()
            post.refresh_from_db()
            total_likes = post.count_likes

        except Relation.DoesNotExist:
            Relation.objects.select_related("user", "post").create(
                user=user, post=post, like=True
            )
            total_likes = post.count_likes
        ctx.update({"total_likes": total_likes})
        return render(request, "components/relations/liked.html", ctx)

    # """  htmx based; user can add and delete items from bookmark  """


class TrackBookmark(LRM, View):
    def post(self, request, *args, **kwargs):
        """
        (ajax)add or (htmx)delete bookmark for logged-in user;
        if delete -> need to reload(update menu via ctx-processors)
        """
        action = kwargs.get("action")
        msg = None
        try:
            post_uuid = request.POST.get("post_uuid", None)
            profile_uuid = request.POST.get("profile_uuid", None)
            post = get_object_or_404(Post, uuid=post_uuid)
            profile = get_object_or_404(Profile, uuid=profile_uuid)

            if action == "add":
                rel, created = Relation.objects.select_related(
                    "user", "post"
                ).get_or_create(
                    user=profile.user, post=post
                )  # noqa
                rel.in_bookmark = True
                rel.save()
                msg = _("Added to bookmark")
                return JsonResponse(
                    {"status_code": 200, "msg": msg, "del_button": True}
                )
            elif self.request.htmx and action == "delete":
                # htmx for delete
                rel = get_object_or_404(Relation, user=profile.user, post=post)
                rel.in_bookmark = False
                rel.save()
                msg = _("Successfully removed from bookmarks")
                # reload: to remove link to bookmaks from menu if no bmark posts
                path_to_go = self.request.headers["Referer"]
                return HttpResponse(
                    status=200,
                    headers={
                        "HX-Redirect": path_to_go,
                    },
                )

        except Post.DoesNotExist:
            if self.request.htmx:
                return HttpResponse(status=404)

            return JsonResponse(
                {"status_code": 404, "msg": _("Failed to change bookmark")}
            )
