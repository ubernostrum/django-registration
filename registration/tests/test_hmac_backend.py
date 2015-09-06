import datetime
import time

from django.contrib.auth.models import User
from django.core import mail
from django.core import signing
from django.core.urlresolvers import reverse
from django.test import override_settings, TestCase

from ..forms import RegistrationForm
from registration.backends.hmac.views import REGISTRATION_SALT


@override_settings(ROOT_URLCONF='registration.backends.hmac.urls')
class SigningBackendViewTests(TestCase):
    """
    Test the signed-token registration workflow.

    Running these tests successfully will require two templates to be
    created for the sending of activation emails; details on these
    templates and their contexts may be found in the documentation for
    the default backend.

    """
    @override_settings(REGISTRATION_OPEN=True)
    def test_registration_open(self):
        """
        ``REGISTRATION_OPEN``, when ``True``, permits registration.

        """
        resp = self.client.get(reverse('registration_register'))
        self.assertEqual(200, resp.status_code)

    @override_settings(REGISTRATION_OPEN=False)
    def test_registration_closed(self):
        """
        ``REGISTRATION_OPEN``, when ``False``, disallows registration.

        """
        resp = self.client.get(reverse('registration_register'))
        self.assertRedirects(resp, reverse('registration_disallowed'))

        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        self.assertRedirects(resp, reverse('registration_disallowed'))

    def test_registration_get(self):
        """
        HTTP ``GET`` to the registration view uses the appropriate
        template and populates a registration form into the context.

        """
        resp = self.client.get(reverse('registration_register'))
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp,
                                'registration/registration_form.html')
        self.assertTrue(isinstance(resp.context['form'],
                        RegistrationForm))

    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_registration(self):
        """
        Registration creates a new inactive account and sends an
        activation email.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        self.assertRedirects(resp, reverse('registration_complete'))

        new_user = User.objects.get(username='bob')

        self.assertTrue(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        # New user must not be active.
        self.assertFalse(new_user.is_active)

        # An activation email was sent.
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_registration_no_sites(self):
        """
        Registration still functions properly when
        ``django.contrib.sites`` is not installed; the fallback will
        be a ``RequestSite`` instance.

        """
        with self.modify_settings(INSTALLED_APPS={
            'remove': [
                'django.contrib.sites'
            ]
        }):
            resp = self.client.post(
                reverse('registration_register'),
                data={'username': 'bob',
                      'email': 'bob@example.com',
                      'password1': 'secret',
                      'password2': 'secret'})
            self.assertEqual(302, resp.status_code)

            new_user = User.objects.get(username='bob')

            self.assertTrue(new_user.check_password('secret'))
            self.assertEqual(new_user.email, 'bob@example.com')

            self.assertFalse(new_user.is_active)

            self.assertEqual(len(mail.outbox), 1)

    def test_registration_failure(self):
        """
        Registering with invalid data fails.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'notsecret'})
        self.assertEqual(200, resp.status_code)
        self.assertFalse(resp.context['form'].is_valid())
        self.assertEqual(0, len(mail.outbox))

    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_activation(self):
        """
        Activation of an account functions properly.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
        activation_key = signer.sign('bob')

        resp = self.client.get(reverse(
            'registration_activate',
            args=(),
            kwargs={'activation_key': activation_key})
        )
        self.assertRedirects(resp, reverse('registration_activation_complete'))

    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_repeat_activation(self):
        """
        Once activated, attempting to re-activate an account (even
        with a valid key) does nothing.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
        activation_key = signer.sign('bob')

        resp = self.client.get(reverse(
            'registration_activate',
            args=(),
            kwargs={'activation_key': activation_key})
        )
        # First activation redirects to success.
        self.assertRedirects(resp, reverse('registration_activation_complete'))

        resp = self.client.get(reverse(
            'registration_activate',
            args=(),
            kwargs={'activation_key': activation_key})
        )

        # Second activation fails.
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')

    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_activation_expired(self):
        """
        An expired account can't be activated.

        """
        self.client.post(reverse('registration_register'),
                         data={'username': 'bob',
                               'email': 'bob@example.com',
                               'password1': 'secret',
                               'password2': 'secret'})

        # We need to create an activation key valid for the username,
        # but with a timestamp > 7 days in the past. This requires
        # monkeypatching time.time() to return that timestamp, since
        # TimestampSigner uses time.time().
        #
        # On Python 3.3+ this is much easier because of the
        # timestamp() method of datetime objects, but since
        # django-registration has to run on Python 2.7, we manually
        # calculate it using a timedelta between the signup date and
        # the UNIX epoch.
        user = User.objects.get(username='bob')
        joined_timestamp = (
            user.date_joined.date() - datetime.date(1970, 1, 1)
        ).total_seconds()
        expired_timestamp = joined_timestamp - (7 * 86400) - 1
        _old_time = time.time
        time.time = lambda: expired_timestamp

        try:
            signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
            activation_key = signer.sign('bob')
        finally:
            time.time = _old_time

        resp = self.client.get(reverse(
            'registration_activate',
            args=(),
            kwargs={'activation_key': activation_key}))

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')

    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_nonexistent_activation(self):
        """
        A nonexistent username in an activation key will fail to
        activate.

        """
        signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
        activation_key = signer.sign('parrot')

        resp = self.client.get(reverse(
            'registration_activate',
            args=(),
            kwargs={'activation_key': activation_key}))

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')
