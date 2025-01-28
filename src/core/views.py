from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.core.utils.base import parse_path


def home(request):
    ctx = {}
    return render(request, "core/home.html", ctx)


def about(request: HttpRequest) -> HttpResponse:
    ctx = {}
    return render(request, "core/about.html", ctx)


def thanks(request: HttpRequest) -> HttpResponse:
    ctx = {}
    return render(request, "core/acknowledgments.html", ctx)


def illenss_script(request: HttpRequest) -> HttpResponse:
    ctx = {}
    lng = parse_path(request)
    if lng == "en":        
        return render(request, "core/eng-illness_scripts.html", ctx)
    return render(request, "core/illness_script.html", ctx)


def problem_presentation(request: HttpRequest) -> HttpResponse:
    ctx = {}
    lng = parse_path(request)
    if lng == "en":
        return render(request, "core/eng-problem_presentation.html", ctx)
    return render(request, "core/problem_presentation.html", ctx)


def pt_script(request: HttpRequest) -> HttpResponse:
    ctx = {}
    lng = parse_path(request)
    if lng == "en":
        return render(request, "core/eng-pt_script.html", ctx)
    return render(request, "core/pt_script.html", ctx)
