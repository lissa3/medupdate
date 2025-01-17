from django.urls import path

from .views import about, illenss_script, problem_presentation, pt_script, thanks

app_name = "core"

urlpatterns = [
    path("acknowledgments/", thanks, name="thanks"),
    path("about/", about, name="about"),
    path("illness-script/", illenss_script, name="illness_script"),
    path("problem-presentaion/", problem_presentation, name="problem_present"),
    path("pt-script/", pt_script, name="pt_script"),
]
