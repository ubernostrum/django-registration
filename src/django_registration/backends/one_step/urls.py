"""
URLconf for registration using django-registration's one-step
workflow.

"""

from django.urls import path
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path(
        "register/",
        views.RegistrationView.as_view(),
        name="django_registration_register",
    ),
    path(
        "register/closed/",
        TemplateView.as_view(
            template_name="django_registration/registration_closed.html"
        ),
        name="django_registration_disallowed",
    ),
    path(
        "register/complete/",
        TemplateView.as_view(
            template_name="django_registration/registration_complete.html"
        ),
        name="django_registration_complete",
    ),
]
