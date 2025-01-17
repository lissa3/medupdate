from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseBadRequest
from django.test import override_settings
from django.urls import reverse
from django_webtest import WebTest

from src.accounts.admin import User
from src.accounts.tests.factories import AdminSupUserFactory, StaffUserFactory
from src.posts.tests.factories import PostFactory


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class TestAdminDevelopers(WebTest):
    def setUp(self):
        self.sup_user = AdminSupUserFactory()
        self.sup_user = AdminSupUserFactory(username="polly")
        self.group = Group.objects.create(name="devs")
        codenames = [
            "add_post",
            "change_post",
            "view_post",
        ]
        permissions = Permission.objects.filter(
            content_type__app_label="posts", codename__in=codenames
        )
        for permission in permissions.all():
            self.group.permissions.add(permission)

        self.staff_author = StaffUserFactory(username="bob")
        self.staff_author.groups.add(self.group)

        self.post_sup_user = PostFactory.create(
            author=self.sup_user,
            title_en="sup user title",
            content_en="sup user notes",
            status=0,
        )
        self.post_staff = PostFactory.create(
            author=self.staff_author,
            title_en="Bell's palsy",
            content_en="infections",
            status=0,
        )
        self.app.set_user(self.staff_author)

    def test_staff_user_can_load_view(self):
        """auth staff user belongs to devs group"""
        dev_group = User.objects.filter(groups__name="devs")

        assert self.staff_author in dev_group

    def test_staff_user_can_view_posts(self):
        """auth staff user can view list of own posts in admin"""
        url = reverse("admin:posts_post_changelist")

        resp = self.app.get(url)
        table_list = resp.html.find("table", id="result_list")
        t_body = table_list.find("tbody")
        rows = t_body.find_all("tr")

        assert resp.status_code == 200
        assert len(rows) == 1

    def test_staff_user_can_edit_own_post(self):
        """auth staff user can edit own posts in admin"""
        url = reverse(
            "admin:posts_post_change", kwargs={"object_id": self.post_staff.id}
        )

        resp = self.app.get(url)

        form = resp.forms["post_form"]
        form["title_en"] = "goblin"

        resp2 = form.submit().follow()

        self.post_staff.refresh_from_db()

        assert resp.status_code == 200
        assert resp2.status_code == 200
        assert self.post_staff.title_en == "goblin"
        assert self.post_staff.content_en == "infections"

    def test_staff_user_can_not_crud_sup_user_post(self):
        """
        logged-in staff user can't edit of superuser;
        msg: Post ....doesn’t exist. Perhaps it was deleted
        """
        url = reverse(
            "admin:posts_post_change", kwargs={"object_id": self.post_sup_user.id}
        )

        resp = self.app.get(url).follow()
        warning = resp.html.find("li", class_="warning")
        text = warning.text

        assert resp.status_code == 200
        assert "deleted" in text

    def test_staff_user_can_not_delete_own_post(self):
        """auth staff user (and post author) has no perms to delete own post"""
        url = reverse(
            "admin:posts_post_delete", kwargs={"object_id": self.staff_author.id}
        )
        resp = self.app.get(url, status=403)
        assert resp.status_code == 403
