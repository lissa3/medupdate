from django.db.models import Case, Count, When

from src.posts.models.relation_model import Relation


def calc_count_likes(obj):
    agr_likes = (
        Relation.objects.select_related("user", "post")
        .filter(post=obj)
        .aggregate(total_likes=(Count(Case(When(like=True, then=1)))))
    )
    obj.count_likes = agr_likes.get("total_likes", None)
    obj.save()


def calc_count_marks(obj):
    agr_bmarks = (
        Relation.objects.select_related("user", "post")
        .filter(post=obj)
        .aggregate(total_bmarks=(Count(Case(When(in_bookmark=True, then=1)))))
    )
    obj.count_bmarks = agr_bmarks.get("total_bmarks", None)
    obj.save()
