"""
URL patterns for the post-1.11 class-based Django auth views.

"""

import textwrap
import warnings

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


urlpatterns = [
    url(r'^login/$',
        auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ),
        name='auth_login'),
    url(r'^logout/$',
        auth_views.LogoutView.as_view(
            template_name='registration/logout.html'
        ),
        name='auth_logout'),
    url(r'^password/change/$',
        auth_views.PasswordChangeView.as_view(
            success_url='auth_password_change_done'
        ),
        name='auth_password_change'),
    url(r'^password/change/done/$',
        auth_views.PasswordChangeDoneView.as_view(),
        name='auth_password_change_done'),
    url(r'^password/reset/$',
        auth_views.PasswordResetView.as_view(
            email_template_name='registration/password_reset_email.txt',
            success_url='auth_password_reset_done',
        ),
        name='auth_password_reset'),
    url(r'^password/reset/complete/$',
        auth_views.PasswordResetCompleteView.as_view(),
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.PasswordResetDoneView.as_view(),
        name='auth_password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/'
        r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            success_url='auth_password_reset_complete'
        ),
        name='auth_password_reset_confirm'),
]
