"""
URL patterns for the views included in ``django.contrib.auth``.

Including these URLs (via the ``include()`` directive) will set up
these patterns based at whatever URL prefix they are included under.

The URLconfs in the built-in registration workflows already have an
``include()`` for these URLs, so if you're using one of them it is not
necessary to manually include these views.

"""
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views


# Django 1.11 introduced class-based auth views with
# backwards-compatible aliases. Using them directly resolves an edge
# case where a password-reset token could be leaked, so we define two
# URLconfs -- one for the old function-based views and one directly
# using the new class-based views -- and select which to use by
# testing for the presence of the class-based views.

auth_url_module = 'registration.auth_urls_classes' if \
                  hasattr(auth_views, 'LoginView') else \
                  'registration.auth_urls_functions'


urlpatterns = [
    url(r'', include(auth_url_module)),
]
