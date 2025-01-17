from django.urls import path

from .views import (
    ChangeState,
    DevDetailPost,
    DevPage,
    MakeNewPost,
    SendNewsLetter,
    ShowDevPostList,
    SoftDeletePost,
)

app_name = "devs"

urlpatterns = [
    path("", DevPage.as_view(), name="dev_page"),
    path("drafts/<action>/", ShowDevPostList.as_view(), name="selection"),
    path(
        "dev-post-detail/<str:uuid>/",
        DevDetailPost.as_view(),
        name="dev_detail_post",
    ),
    path("soft-delete/<str:uuid>/", SoftDeletePost.as_view(), name="soft_delete_post"),
    path("change-state/<action>/", ChangeState.as_view(), name="change_state"),
    path("creation/", MakeNewPost.as_view(), name="creation"),
    path("sending-news-letter/", SendNewsLetter.as_view(), name="celery-letter"),
]
