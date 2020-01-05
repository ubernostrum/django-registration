"""
URLs used to test the activation workflow with a custom user
model.

You should not use these in any sort of real environment.

"""

from django.urls import path
from django.views.generic.base import TemplateView

from django_registration.backends.activation import views
from django_registration.forms import RegistrationForm

from ..models import CustomUser


class CustomUserRegistrationForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = CustomUser


urlpatterns = [
    path(
        "activate/complete/",
        TemplateView.as_view(
            template_name="django_registration/activation_complete.html"
        ),
        name="django_registration_activation_complete",
    ),
    path(
        "activate/<str:activation_key>/",
        views.ActivationView.as_view(),
        name="django_registration_activate",
    ),
    path(
        "register/",
        views.RegistrationView.as_view(form_class=CustomUserRegistrationForm),
        name="django_registration_register",
    ),
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
