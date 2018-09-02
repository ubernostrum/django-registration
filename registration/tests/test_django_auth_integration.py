from re import search as re_search

from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.core import mail
from django.test import TestCase, modify_settings, override_settings


try:
    from unittest.mock import ANY, patch
except ImportError:
    from mock import ANY, patch

try:
    from django.contrib.auth.views import (
        INTERNAL_RESET_URL_TOKEN,
    )
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
    INTERNAL_RESET_URL_TOKEN = 'set-password'


def buildTemplateSettings():
    template_settings = settings.TEMPLATES[0]
    template_settings['APP_DIRS'] = True
    return template_settings


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('registration.backends.hmac.urls')),
]


@modify_settings(INSTALLED_APPS={
    'remove': 'registration'})
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

    def test_password_change(self):
        """Simulate user password change

        A user logs in, accesses a page, POSTs a new password to change
        the password.

        Regression test for #106 - ensure redirect after POST works

        https://github.com/ubernostrum/django-registration/issues/106

        """
        newpassword = 'neo.h1m1tsu!'
        pw_change_url = reverse('auth_password_change')

        # Step 1 - access the password change URL
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(pw_change_url)
        # WARNING: uses Django's admin template
        self.assertTemplateUsed(
            response, 'registration/password_change_form.html')

        # Step 2 - POST existing and new password to change password
        data = {
            'old_password': self.password,
            'new_password1': newpassword,
            'new_password2': newpassword,
        }
        response = self.client.post(pw_change_url, data=data, follow=True)
        self.assertRedirects(response, reverse('auth_password_change_done'))
        self.assertEqual(response.status_code, 200)
        # WARNING: uses Django's admin template
        self.assertTemplateUsed(
            response, 'registration/password_change_done.html')

        # Check that new password properly set
        self.client.logout()
        self.assertTrue(
            self.client.login(username=self.username, password=newpassword))

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

    def test_password_reset(self):
        """Simulate user password reset

        The user starts by requesting a password reset: they load a
        page, and POST their email to the site. This redirects them to a
        page informing them to expect an email. An email is sent to the
        provided email address, providing the user with a special URL.
        The page at this URL asks them for a new password. Once
        POSTed, the user is then redirected one last time.

        Regression test for #106 - ensure all redirects work correctly

        https://github.com/ubernostrum/django-registration/issues/106

        """
        newpassword = 'neo.h1m1tsu!'
        pw_reset_url = reverse('auth_password_reset')

        # Step 1 - load the password reset page
        response = self.client.get(pw_reset_url)
        self.assertEqual(response.status_code, 200)
        # WARNING: uses Django's admin template
        self.assertTemplateUsed(
            response, 'registration/password_reset_form.html')

        # Step 2 - request password reset URL at specific email
        data = {'email': self.email}
        post_response = self.client.post(pw_reset_url, data=data, follow=True)
        self.assertRedirects(
            post_response, reverse('auth_password_reset_done'))
        # WARNING: uses Django's admin template
        self.assertTemplateUsed(
            post_response, 'registration/password_reset_done.html')

        # Step 3 - receive email with link back to site for reset
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.email])
        self.assertEqual(
            mail.outbox[0].subject, 'Password reset on example.com')
        urlmatch = re_search(r'https?://[^/]*(/.*reset/\S*)',
                             mail.outbox[0].body)
        self.assertIsNotNone(urlmatch, 'No URL found in sent email')
        url_path = urlmatch.groups()[0]
        uidb64, token = list(filter(None, url_path.split('/')))[-2:]
        self.assertEqual(
            reverse('auth_password_reset_confirm',
                    kwargs={'uidb64': uidb64, 'token': token}),
            url_path)

        # Step 4 - Access URL provided in reset email
        # TODO: remove condition when Django 1.10 dropped
        if DJANGO_VERSION >= (1, 11):
            # Django class-based auth views redirects to a URL without a
            # token to prevent leaking the token to third-parties
            reset_get_response = self.client.get(url_path)
            self.assertRedirects(
                reset_get_response,
                reverse('auth_password_reset_confirm',
                        kwargs={
                            'uidb64': uidb64,
                            'token': INTERNAL_RESET_URL_TOKEN}))
            url_path = reset_get_response.url
        reset_get_response = self.client.get(url_path)
        self.assertEqual(reset_get_response.status_code, 200)
        # WARNING: uses Django's admin template
        self.assertTemplateUsed(
            reset_get_response, 'registration/password_reset_confirm.html')

        # Step 5 - Reset Password in Form
        data = {
            'new_password1': newpassword,
            'new_password2': newpassword,
        }
        reset_post_response = self.client.post(
            url_path, data=data, follow=True)
        self.assertRedirects(
            reset_post_response, reverse('auth_password_reset_complete'))

        # Ensure that Password Reset Worked Correct
        self.assertTrue(
            self.client.login(username=self.username, password=newpassword))
