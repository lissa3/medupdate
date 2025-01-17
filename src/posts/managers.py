from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.db.models import QuerySet


class PostFilterManager(QuerySet):
    def get_drafts(self):
        """
        filter qs for posts in draft(in progress)
        """
        return self.filter(status=0, is_deleted=False)

    def get_review(self):
        """filter qs for posts in review"""
        return self.select_related("author", "categ", "letter", "video").filter(
            status=1, is_deleted=False
        )

    def get_public(self):
        """filter qs for public posts"""
        return (
            self.select_related("author", "categ", "letter")
            .prefetch_related("tags", "pics")
            .filter(status=2, is_deleted=False)
        ).order_by("-published_at")

    def get_soft_deleted(self):
        """
        filter qs for soft deleted;
        posts can have diff status
        """
        return self.filter(is_deleted=True)

    def search_uk(self, query_text=""):
        """search for ukrainian lang"""
        vector = SearchVector("content_uk", weight="B") + SearchVector(
            "title_uk", weight="A"
        )
        search_query = SearchQuery(query_text)
        search_rank = SearchRank(vector, search_query)
        search_headline = SearchHeadline(
            "content_uk",
            search_query,
        )
        return (
            self.select_related("author", "categ", "letter")
            .filter(status=2, is_deleted=False)
            .annotate(search=vector, headline=search_headline)
            .filter(search=search_query)
            .annotate(rank=search_rank)
            .order_by("-rank")
        )
