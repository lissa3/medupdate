from django.contrib import messages
from django.db.models import F
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, TemplateView, View

from src.contacts.models import NewsLetter
from src.core.tasks import post_letter
from src.posts.models.post_model import Post

from .mixins import RestricToAuthorMixin as RTA
from .mixins import StaffUserRequiredMixin as SURM

actions_dict = {
    0: "draft",
    1: "review",
}


class DevPage(SURM, TemplateView):
    """
    SURM but now accessable only by superuser (via menu.html)
    If devs(+) change it?
    """

    template_name = "devs/dev_dashboard.html"

    def get_context_data(self, **kwargs) -> dict:
        """
        now only superuser has a link to admin via menu(dashboard);
        if devs(+) may be add it menu and  add check has_perm("posts.add_post")
        """
        ctx = super().get_context_data(**kwargs)
        if self.request.user.has_perm("posts.delete_post"):
            ctx["to_admin_link"] = reverse("admin:posts_post_changelist")
        return ctx


class ShowDevPostList(SURM, ListView):
    """
    private page to display list of posts in status:
    draft/review or soft deleted;
    is_staff can access their own posts;
    superuser - all posts via  to_admin link
    """

    template_name = "devs/dev_post_list.html"
    context_object_name = "posts"
    paginate_by = 12
    to_admin_link = False
    header = ""

    def get_queryset(self):
        is_super_user = self.request.user.is_superuser
        action = self.kwargs.get("action", "unknown-action")
        if action == "draft":
            self.header = "Posts in draft"
            if is_super_user:
                return Post.objects.get_drafts()
            return Post.objects.get_drafts().filter(author=self.request.user)
        elif action == "review":
            self.header = "Posts in  review"
            if is_super_user:
                return Post.objects.get_review()
            return Post.objects.get_review().filter(author=self.request.user)
        elif action == "soft_delete":
            self.header = "Posts in soft deleted"
            if is_super_user:
                return Post.objects.get_soft_deleted()
            return Post.objects.get_soft_deleted().filter(author=self.request.user)

        else:
            return Http404

    def get_context_data(self, **kwargs):
        """author can see in admin their permitted objects"""
        ctx = super().get_context_data(**kwargs)
        ctx["header"] = self.header
        return ctx


class DevDetailPost(SURM, RTA, DetailView):
    model = Post
    context_object_name = "post"
    template_name = "devs/dev_post_detail.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"


class ShowDeletedPosts(SURM, ListView):
    """show soft-deleted posts"""

    template_name = "devs/dev_post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        return Post.show_soft_deleted.filter(author=self.request.user)

    def get_success_url(self) -> str:
        """obj draft vs review"""
        if self.get_object().status == 0:
            action = "draft"
        else:
            action = "review"
        return reverse_lazy("posts:dev_posts", kwargs={"action": f"{action}"})


class ChangeState(SURM, View):
    """
    not public post  can change it's current state:
    - soft-delted -> withdraw soft-del
    - in progress -> preview
    - in preview  -> published
    Depending on action -> redirect to dashboard (public) or
    corresp list of posts (review/soft deleted)
    """

    def post(self, request, **kwargs):
        uuid = request.POST.get("uuid", None)
        current_state = request.POST.get("current_state")
        post = get_object_or_404(
            Post, uuid=uuid, status=current_state, author=self.request.user
        )
        url_dash = reverse_lazy("devs:dev_page")
        action = self.kwargs.get("action")
        if action == "status":
            post.status = F("status") + 1
            post.save()
            post.refresh_from_db()
            new_status = post.get_status_display()

            messages.add_message(
                request,
                messages.SUCCESS,
                f"Successfully changed level to: {new_status}",
                fail_silently=True,
            )
            if post.status == 1:
                new_action = "review"
                url = reverse_lazy("devs:selection", kwargs={"action": new_action})
                return HttpResponseRedirect(url)
            else:
                return HttpResponseRedirect(url_dash)
        elif action == "remove_soft_del":
            post.is_deleted = False
            post.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "soft-deleted is withdrawn",
                fail_silently=True,
            )
            new_action = actions_dict[post.status]
            url = reverse_lazy("devs:selection", kwargs={"action": f"{new_action}"})

            return HttpResponseRedirect(url)


class SoftDeletePost(SURM, RTA, DeleteView):
    """
    only to soft delete; use admin to delete permanently;
    after applying changes -> redirect the corresp action list
    """

    model = Post
    template_name = "devs/dev_post_detail.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def form_valid(self, form):
        obj = self.get_object()
        obj.is_deleted = True
        obj.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        """obj draft vs review"""
        action = "soft_delete"
        return reverse_lazy("devs:selection", kwargs={"action": f"{action}"})


class MakeNewPost(SURM, View):
    def get(self, request):
        return render(request, "devs/creation.html")


class SendNewsLetter(SURM, View):
    def get(self, request):
        """
        check in template if superuser -> button celery task
        """
        # post_letter.delay()
        url = reverse_lazy("devs:dev_page")
        # let = NewsLetter.objects.filter(letter_status=1).last()
        messages.add_message(
            request,
            messages.SUCCESS,
            "Waking up celery daemon",
            fail_silently=True,
        )
        return HttpResponseRedirect(url)
