import logging

from django.contrib.postgres.search import SearchQuery
from django.http import HttpResponse
from django.shortcuts import render

from src.posts.models.post_model import Post

logger = logging.getLogger("project")


def clear(request):
    """(htmx) help func to clean elem on htmx requests"""
    return HttpResponse("")


def make_query(current_lang, user_inp):
    """
    separated query config;
    (no postgres config for ukrainian to make a trigger)
    """
    lang_dict = {"en": "english", "ru": "russian", "nl": "dutch"}
    if current_lang != "uk":
        query = SearchQuery(
            user_inp, config=lang_dict[current_lang], search_type="websearch"
        )
    else:
        query = user_inp
    return query


def search_qs(current_lang, query):
    """
    split diff lang for search
    """
    if current_lang == "uk":
        posts = Post.objects.search_uk(query_text=query)
    elif current_lang == "en":
        posts = Post.objects.get_public().filter(vector_en=query)
    elif current_lang == "ru":
        posts = Post.objects.get_public().filter(vector_ru=query)

    return posts


def terms(request):
    """show terms and conditions by sign-up"""

    return render(request, "core/terms_conditions.html")


def get_ip(req):
    """
    if x_forward present return it;
    otherwise remote_addr or empty string
    """
    try:
        forward = req.META.get("HTTP_X_FORWARDED_FOR")
        if forward:
            return (
                req.META.get("HTTP_X_FORWARDED_FOR", req.META.get("REMOTE_ADDR", ""))
                .split(",")[0]
                .strip()
            )
        else:
            return req.META.get("REMOTE_ADDR")

    except Exception as e:
        logger.warning(f"Failed to find IP in request: {e}")
        return ""
