"""
URLs used in the unit tests for django-registration.

You should not attempt to use these URLs in any sort of real or
development environment.

"""

from django.urls import path
from django.views.generic.base import TemplateView

from django_registration.backends.activation.views import RegistrationView

from ..views import ActivateWithComplexRedirect


urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="django_registration/activation_complete.html"
        ),
        name="simple_activation_redirect",
    ),
    path(
        "activate/complete/",
        TemplateView.as_view(
            template_name="django_registration/activation_complete.html"
        ),
        name="django_registration_activation_complete",
    ),
    path(
        "activate/<str:activation_key>/",
        ActivateWithComplexRedirect.as_view(),
        name="django_registration_activate",
    ),
    path("register/", RegistrationView.as_view(), name="django_registration_register"),
    path(
        "register/complete/",
        TemplateView.as_view(
            template_name="django_registration/registration_complete.html"
        ),
        name="django_registration_complete",
    ),
    path(
        "register/closed/",
        TemplateView.as_view(
            template_name="django_registration/registration_closed.html"
        ),
        name="django_registration_disallowed",
    ),
]
