from django.test import TestCase, override_settings
from django.urls import reverse

from src.accounts.tests.factories import AdminSupUserFactory
from src.posts.models.categ_model import Category
from src.posts.tests.factories import CategoryFactory


@override_settings(LANGUAGE_CODE="en", LANGUAGES=(("en", "English"),))
class TestAdminCategoryForm(TestCase):
    def setUp(self):
        self.user = AdminSupUserFactory()
        self.client.force_login(self.user)

    def test_create_root_category_admin(self):
        count_start = Category.objects.count()
        url = reverse("admin:posts_category_add")
        data = {
            "name_ru": "Сердечно-Сосудистая",
            "name_en": "Cardio",
            "_position": "sorted-child",
        }
        resp = self.client.post(url, data=data)

        count_end = Category.objects.count()
        categ = Category.objects.last()
        self.assertEqual(resp.status_code, 302)
        self.assertLess(count_start, count_end)
        self.assertEqual(categ.name_en, "Cardio")
        self.assertEqual(categ.is_root(), True)

    def test_child_category_admin(self):
        categ_root = CategoryFactory(name="grand_pa")
        count_start = Category.objects.count()
        url = reverse("admin:posts_category_add")
        data = {
            "name_ru": "Сердечно-Сосудистая",
            "name_en": "Cardio",
            "_position": "sorted-child",
            "_ref_node_id": categ_root.id,
        }
        resp = self.client.post(url, data=data)

        count_end = Category.objects.count()
        categ = Category.objects.last()
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(count_start, 1)
        self.assertEqual(count_end, 2)
        self.assertEqual(categ.name_en, "Cardio")
        self.assertFalse(categ.is_root())
