from django.test import TestCase

from src.posts.models.post_model import Post

from .factories import PostFactory


class PostCreationTestCase(TestCase):
    def setUp(self) -> None:
        # published/in review/drafts(in progress)
        PostFactory.create_batch(2, status=Post.CurrentStatus.PUB.value)
        PostFactory.create_batch(3, status=Post.CurrentStatus.REVIEW.value)
        PostFactory.create_batch(4, status=Post.CurrentStatus.DRAFT.value)

    def test_public_posts(self):
        public_posts_count = Post.objects.get_public().count()
        posts_in_review_count = Post.objects.get_review().count()
        posts_drafts_count = Post.objects.get_drafts().count()

        self.assertEqual(public_posts_count, 2)
        self.assertEqual(posts_drafts_count, 4)
        self.assertEqual(posts_in_review_count, 3)

    def test_soft_deleted(self):
        """soft delete one post in drafts"""
        drafts = Post.objects.get_drafts()
        drafts_count_before = drafts.count()

        obj_to_soft_delete = drafts.first()
        obj_to_soft_delete.soft_delete()

        drafts_count_after = drafts.count()

        self.assertNotEqual(drafts_count_before, drafts_count_after)
