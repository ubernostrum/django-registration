from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.test import TestCase, modify_settings, override_settings


try:
    from unittest.mock import ANY, patch
except ImportError:  # pragma: no cover
    from mock import ANY, patch  # pragma: no cover

try:
    from django.urls import reverse
except ImportError:  # pragma: no cover
    from django.core.urlresolvers import reverse  # pragma: no cover


def buildTemplateSettings():
    template_settings = settings.TEMPLATES[0]
    template_settings['APP_DIRS'] = True
    return template_settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
]


@modify_settings(INSTALLED_APPS={
    'prepend': ['django.contrib.admin'], 'remove': 'registration'})
@override_settings(
    ROOT_URLCONF='registration.tests.test_django_auth_integration')
@override_settings(TEMPLATES=[buildTemplateSettings()])
class DjangoAuthURLTests(TestCase):
    """Tests for the auth URLs imported by django-registration"""

    @classmethod
    def setUpClass(cls):
        """Create user for testing purposes"""
        super(DjangoAuthURLTests, cls).setUpClass()
        cls.username = 'Tester'
        cls.email = 'test@djangoproject.org'
        cls.password = 'password1!'
        User = get_user_model()
        User.objects.create_user(cls.username, cls.email, cls.password)

    @patch.object(PasswordResetForm, 'send_mail')
    def test_password_reset_email(self, send_mail_mock):
        """Regression test for #113

        https://github.com/ubernostrum/django-registration/issues/113

        Ensures that the email template used in versions of
        django-registration across Django versions is the same.

        """
        pw_reset_name = 'auth_password_reset'
        # ensure view exists
        pw_reset_get_response = self.client.get(reverse(pw_reset_name))
        self.assertEqual(pw_reset_get_response.status_code, 200)
        # post data to password reset; make Django send email
        data = {'email': self.email}
        self.client.post(reverse(pw_reset_name), data=data, follow=True)
        # verify that email sent with right template
        send_mail_mock.assert_called_with(
            ANY,
            'registration/password_reset_email.txt',
            ANY, ANY, ANY,
            html_email_template_name=ANY)
