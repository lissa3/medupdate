from django.urls import path

from .views import (
    DeleteCommentView,
    GetReplyFormView,
    ProccessReplyView,
    display_all_comments,
    display_selected_comments,
    handle_edit_comment,
)

app_name = "comments"


# all htmx_urlpatterns
urlpatterns = [
    path("all-comms/<post_uuid>/", display_all_comments, name="all_comms"),
    # let op: flag
    path(
        "all-comms-notifs/<post_uuid>/<notif_flag>/",
        display_all_comments,
        name="all_comms_notifs",
    ),
    path(
        "selected-thread/<post_uuid>/<thread_uuid>/",
        display_selected_comments,
        name="select_comms",
    ),
    # create
    path(
        "add-comm/<post_uuid>/<comm_id>/", GetReplyFormView.as_view(), name="add_comm"
    ),
    path(
        "process-reply/<post_uuid>/", ProccessReplyView.as_view(), name="process_comm"
    ),
    # delete
    path(
        "process-delete/<post_uuid>/<comm_id>/",
        DeleteCommentView.as_view(),
        name="handle_delete",
    ),
    # edit
    path("edit-comm/<post_uuid>/<comm_id>/", handle_edit_comment, name="handle_edit"),
]
