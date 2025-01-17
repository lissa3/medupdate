from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from src.posts.models.media_model import Video


def home(request):
    ctx = {}
    # vidos = get_object_or_404(Video, id=1)
    # if vidos:
    #     ctx = {"vidos": vidos}
    return render(request, "core/home.html", ctx)


def about(request: HttpRequest) -> HttpResponse:
    ctx = {}
    return render(request, "core/about.html", ctx)


def thanks(request: HttpRequest) -> HttpResponse:
    ctx = {}
    return render(request, "core/acknowledgments.html", ctx)


def illenss_script(request: HttpRequest) -> HttpResponse:
    ctx = {}
    return render(request, "core/illness_script.html", ctx)


def problem_presentation(request: HttpRequest) -> HttpResponse:
    ctx = {}
    # vidos = get_object_or_404(Video, id=2)
    # if vidos:
    #     ctx = {"vidos": vidos}
    return render(request, "core/problem_presentation.html", ctx)


def pt_script(request: HttpRequest) -> HttpResponse:
    ctx = {}
    return render(request, "core/pt_script.html", ctx)
