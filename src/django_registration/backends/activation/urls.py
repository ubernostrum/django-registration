"""
URLconf for registration and activation, using django-registration's
HMAC activation workflow.

"""

from django.conf.urls import url
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    url(r'^activate/complete/$',
        TemplateView.as_view(
            template_name='django_registration/activation_complete.html'
        ),
        name='django_registration_activation_complete'),
    # The activation key can make use of any character from the
    # URL-safe base64 alphabet, plus the colon as a separator.
    url(r'^activate/(?P<activation_key>[-:\w]+)/$',
        views.ActivationView.as_view(),
        name='django_registration_activate'),
    url(r'^register/$',
        views.RegistrationView.as_view(),
        name='django_registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(
            template_name='django_registration/registration_complete.html'
        ),
        name='django_registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(
            template_name='django_registration/registration_closed.html'
        ),
        name='django_registration_disallowed'),
]
