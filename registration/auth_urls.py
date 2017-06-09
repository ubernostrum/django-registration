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

import django

from django.conf.urls import url
from django.contrib.auth import views as auth_views


warnings.warn(
    textwrap.dedent("""
        include('registration.auth_urls') is deprecated and will be
        removed in django-registration 3.0. Use
        include('django.contrib.auth.urls') instead.
    """),
    DeprecationWarning
)

if django.VERSION >= (1, 11):
    urlpatterns = [
        url(r'^login/$',
            auth_views.LoginView.as_view(
                template_name='registration/login.html'),
            name='auth_login'),
        url(r'^logout/$',
            auth_views.LogoutView.as_view(
                template_name='registration/logout.html'),
            name='auth_logout'),
        url(r'^password/change/$',
            auth_views.PasswordChangeView.as_view(
                success_url='auth_password_change_done'),
            name='auth_password_change'),
        url(r'^password/change/done/$',
            auth_views.PasswordChangeDoneView.as_view(),
            name='auth_password_change_done'),
        url(r'^password/reset/$',
            auth_views.PasswordResetView.as_view(
                success_url='auth_password_reset_done'),
            name='auth_password_reset'),
        url(r'^password/reset/complete/$',
            auth_views.PasswordResetCompleteView.as_view(),
            name='auth_password_reset_complete'),
        url(r'^password/reset/done/$',
            auth_views.PasswordResetDoneView.as_view(),
            name='auth_password_reset_done'),
        url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
            auth_views.PasswordResetConfirmView.as_view(
                success_url='auth_password_reset_complete'),
            name='auth_password_reset_confirm'),
    ]
else:
    urlpatterns = [
        url(r'^login/$',
            auth_views.login,
            {'template_name': 'registration/login.html'},
            name='auth_login'),
        url(r'^logout/$',
            auth_views.logout,
            {'template_name': 'registration/logout.html'},
            name='auth_logout'),
        url(r'^password/change/$',
            auth_views.password_change,
            {'post_change_redirect': 'auth_password_change_done'},
            name='auth_password_change'),
        url(r'^password/change/done/$',
            auth_views.password_change_done,
            name='auth_password_change_done'),
        url(r'^password/reset/$',
            auth_views.password_reset,
            {'post_reset_redirect': 'auth_password_reset_done'},
            name='auth_password_reset'),
        url(r'^password/reset/complete/$',
            auth_views.password_reset_complete,
            name='auth_password_reset_complete'),
        url(r'^password/reset/done/$',
            auth_views.password_reset_done,
            name='auth_password_reset_done'),
        url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
            auth_views.password_reset_confirm,
            {'post_reset_redirect': 'auth_password_reset_complete'},
            name='auth_password_reset_confirm'),
    ]
