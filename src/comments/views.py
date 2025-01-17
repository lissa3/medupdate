from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin as LRM
from django.http import HttpResponse, HttpResponseForbidden, QueryDict
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View

from src.comments.forms import CommentForm
from src.comments.mixins import CheckRequestMixin
from src.comments.models import Comment
from src.notifications.models import Notification
from src.posts.models.post_model import Post


def display_all_comments(request, post_uuid, notif_flag=None):
    """htmx based;  triggered via events:
    loaded post page or updated comments after crud"""
    post = Post.objects.get(uuid=post_uuid)
    post_comms = Comment.objects.select_related("post", "user", "reply_to").filter(
        post=post
    )
    if notif_flag is not None and int(notif_flag) == 1:
        _notifs = Notification.objects.filter(post=post, recipient=request.user)
        _notifs.update(read=True)
    return render(
        request,
        "components/comms/wraps.html",
        {"comments": post_comms, "post": post, "user": request.user},
    )


def display_selected_comments(request, post_uuid, thread_uuid):
    """
    htmx based;
    triggered from dropdown-menu link:
    comments refer to replied comment and it's children
    """
    post = Post.objects.get(uuid=post_uuid)
    post_comms = Comment.objects.select_related("post", "user", "reply_to").filter(
        post=post, uuid=thread_uuid
    )
    return render(
        request,
        "components/comms/wraps.html",
        {"comments": post_comms, "post": post, "user": request.user},
    )


class GetReplyFormView(LRM, CheckRequestMixin, View):
    def get(self, request, post_uuid, comm_id):
        """
        if user not banned: add form for reply;
        htmx + modal;
        """
        form = CommentForm(initial={"comm_parent_id": comm_id})
        ctx = {}
        ctx["form"] = form
        ctx["post_uuid"] = post_uuid
        return render(request, "components/comms/comm_form.html", ctx)


class ProccessReplyView(LRM, CheckRequestMixin, View):
    def post(self, request, post_uuid):
        """
        htmx-modal;
        no notifications in cases:
        - parent(replied) comm is deleted;
        - users comment their own comment
        """
        form = CommentForm(request.POST)
        if form.is_valid():
            comm_parent_id = form.cleaned_data["comm_parent_id"]
            post = get_object_or_404(Post, uuid=post_uuid)
            # TODO: check for parent comm is_deleted
            parent_comm = get_object_or_404(Comment, id=comm_parent_id)
            replied_to = parent_comm.user
            comm = form.save(commit=False)
            comm_body = form.cleaned_data["body"]
            comm.user = request.user
            comm.reply_to = replied_to
            comm.post = post
            comm.body = comm_body
            if replied_to == request.user:
                comm.own_reply = True
            parent_comm.add_child(instance=comm)
            return HttpResponse(status=204, headers={"HX-Trigger": "updateCommList"})


@login_required
def handle_edit_comment(request, post_uuid, comm_id):
    """htmx based + modal UI in bootstrap5"""
    if request.user.banned:
        return HttpResponseForbidden()
    ctx = {"post_uuid": post_uuid, "comm_id": comm_id}
    post = get_object_or_404(Post, uuid=post_uuid)
    obj = get_object_or_404(Comment, post_id=post.id, id=comm_id)
    parent = obj.get_parent()
    if request.method == "GET":
        if parent:
            form = CommentForm(instance=obj, initial={"comm_parent_id": comm_id})
        else:
            form = CommentForm(instance=obj)
        ctx["form"] = form
        return render(request, "components/comms/comm_edit_form.html", ctx)
    if request.method == "PUT":
        data_dict = QueryDict(request.body).dict()
        form = CommentForm(data_dict, instance=obj)
        if form.is_valid():
            obj.updated_at = timezone.now()
            obj.edited = True
            obj.save()
            return HttpResponse(status=204, headers={"HX-Trigger": "updateCommList"})
        else:
            ctx["form"] = form
    return render(request, "components/comms/comm_edit_form.html", ctx)


class DeleteCommentView(LRM, CheckRequestMixin, View):
    def get(self, request, post_uuid, comm_id):
        """render modal to confirm"""
        ctx = {"post_uuid": post_uuid, "comm_id": comm_id}
        return render(request, "components/comms/del_confirm.html", ctx)

    def post(self, request, post_uuid, comm_id):
        post = get_object_or_404(Post, uuid=post_uuid)
        comm_to_del = get_object_or_404(Comment, id=comm_id, post_id=post.id)
        comm_to_del.deleted = True
        comm_to_del.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "updateCommList"})
