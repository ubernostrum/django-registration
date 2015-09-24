"""
URLs used in the unit tests for django-registration.

You should not attempt to use these URLs in any sort of real or
development environment.

"""

from django.conf.urls import include, url
from django.views.generic.base import TemplateView

from registration.backends.model_activation.views import RegistrationView

from .views import ActivateWithSimpleRedirect


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
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to
    # the view; that way it can return a sensible "invalid key"
    # message instead of a confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        ActivateWithSimpleRedirect.as_view(),
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
    url(r'', include('registration.auth_urls')),
]
