"""
URL patterns for the views included in ``django.contrib.auth``.

Including these URLs (via the ``include()`` directive) will set up
these patterns based at whatever URL prefix they are included under.

The URLconfs in the built-in registration workflows already have an
``include()`` for these URLs, so if you're using one of them it is not
necessary to manually include these views.

"""
import textwrap
import warnings

from django.conf.urls import include, url
from django.contrib.auth import views as auth_views


warnings.warn(
    textwrap.dedent("""
        include('registration.auth_urls') is deprecated and will be
        removed in django-registration 3.0. Use
        include('django.contrib.auth.urls') instead.
    """),
    DeprecationWarning
)


auth_url_module = 'registration.auth_urls_classes' if \
                  hasattr(auth_views, 'LoginView') else \
                  'registration.auth_urls_functions'


urlpatterns = [
    url(r'', include(auth_url_module)),
]
