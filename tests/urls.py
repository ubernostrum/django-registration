"""
URLs used in the unit tests for django-registration.

You should not attempt to use these URLs in any sort of real or
development environment.

"""

from django.conf.urls import url
from django.views.generic.base import TemplateView

from django_registration.backends.hmac.views import RegistrationView

from .views import ActivateWithComplexRedirect


urlpatterns = [
    url(r'^$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'
        ),
        name='simple_activation_redirect'),
    url(r'^activate/complete/$',
        TemplateView.as_view(
            template_name='registration/activation_complete.html'
        ),
        name='registration_activation_complete'),
    # The activation key can make use of any character from the
    # URL-safe base64 alphabet, plus the colon as a separator.
    url(r'^activate/(?P<activation_key>[-:\w]+)/$',
        ActivateWithComplexRedirect.as_view(),
        name='registration_activate'),
    url(r'^register/$',
        RegistrationView.as_view(),
        name='registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(
            template_name='registration/registration_complete.html'
        ),
        name='registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(
            template_name='registration/registration_closed.html'
        ),
        name='registration_disallowed'),
]
