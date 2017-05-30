"""
URLconf for registration using django-registration's one-step
workflow.

"""

from django.conf.urls import include, url
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    url(r'^register/$',
        views.RegistrationView.as_view(),
        name='registration_register'),
    url(r'^register/closed/$',
        TemplateView.as_view(
            template_name='registration/registration_closed.html'
        ),
        name='registration_disallowed'),
    url(r'', include('registration.auth_urls')),
]
