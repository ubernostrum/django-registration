"""
Tests for the HMAC signed-token registration workflow.

"""

import datetime
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail, signing
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from registration.backends.hmac.views import REGISTRATION_SALT

from ..forms import RegistrationForm


User = get_user_model()


@override_settings(
    ROOT_URLCONF='registration.backends.hmac.urls',
    ACCOUNT_ACTIVATION_DAYS=7,
    REGISTRATION_OPEN=True
)
class HMACViewTests(TestCase):
    """
    Tests for the signed-token registration workflow.

    """
    valid_data = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password1': 'secret',
        'password2': 'secret',
    }

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
        resp = self.client.get(
            reverse('registration_register')
        )
        self.assertRedirects(resp, reverse('registration_disallowed'))

        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )
        self.assertRedirects(resp, reverse('registration_disallowed'))

    def test_registration_get(self):
        """
        HTTP ``GET`` to the registration view uses the appropriate
        template and populates a registration form into the context.

        """
        resp = self.client.get(reverse('registration_register'))
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(
            resp, 'registration/registration_form.html'
        )
        self.assertTrue(
            isinstance(
                resp.context['form'], RegistrationForm
            )
        )

    def test_registration(self):
        """
        Registration creates a new inactive account and sends an
        activation email.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )
        self.assertRedirects(resp, reverse('registration_complete'))

        new_user = User.objects.get(username=self.valid_data['username'])

        self.assertTrue(
            new_user.check_password(
                self.valid_data['password1']
            )
        )
        self.assertEqual(new_user.email, self.valid_data['email'])

        # New user must not be active.
        self.assertFalse(new_user.is_active)

        # An activation email was sent.
        self.assertEqual(len(mail.outbox), 1)

    def test_registration_no_sites(self):
        """
        Registration still functions properly when
        ``django.contrib.sites`` is not installed; the fallback will
        be a ``RequestSite`` instance.

        """
        with self.modify_settings(INSTALLED_APPS={
            'remove': ['django.contrib.sites']
        }):
            resp = self.client.post(
                reverse('registration_register'),
                data=self.valid_data
            )
            self.assertEqual(302, resp.status_code)

            new_user = User.objects.get(username=self.valid_data['username'])

            self.assertTrue(
                new_user.check_password(
                    self.valid_data['password1']
                )
            )
            self.assertEqual(new_user.email, self.valid_data['email'])

            self.assertFalse(new_user.is_active)

            self.assertEqual(len(mail.outbox), 1)

    def test_registration_failure(self):
        """
        Registering with invalid data fails.

        """
        data = self.valid_data.copy()
        data.update(password2='notsecret')
        resp = self.client.post(
            reverse('registration_register'),
            data=data
        )
        self.assertEqual(200, resp.status_code)
        self.assertFalse(resp.context['form'].is_valid())
        self.assertEqual(0, len(mail.outbox))

    def test_activation(self):
        """
        Activation of an account functions properly.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
        activation_key = signer.sign(self.valid_data['username'])

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': activation_key}
            )
        )
        self.assertRedirects(resp, reverse('registration_activation_complete'))

    def test_repeat_activation(self):
        """
        Once activated, attempting to re-activate an account (even
        with a valid key) does nothing.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
        activation_key = signer.sign(self.valid_data['username'])

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': activation_key}
            )
        )
        # First activation redirects to success.
        self.assertRedirects(resp, reverse('registration_activation_complete'))

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': activation_key}
            )
        )

        # Second activation fails.
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')

    def test_activation_expired(self):
        """
        An expired account can't be activated.

        """
        self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        # We need to create an activation key valid for the username,
        # but with a timestamp > ACCOUNT_ACTIVATION_DAYS days in the
        # past. This requires monkeypatching time.time() to return
        # that timestamp, since TimestampSigner uses time.time().
        #
        # On Python 3.3+ this is much easier because of the
        # timestamp() method of datetime objects, but since
        # django-registration has to run on Python 2.7, we manually
        # calculate it using a timedelta between the signup date and
        # the UNIX epoch, and patch time.time() temporarily to return
        # a date (ACCOUNT_ACTIVATION_DAYS + 1) days in the past.
        user = User.objects.get(username=self.valid_data['username'])
        joined_timestamp = (
            user.date_joined - datetime.datetime.fromtimestamp(0)
        ).total_seconds()
        expired_timestamp = (
            joined_timestamp - (settings.ACCOUNT_ACTIVATION_DAYS + 1) * 86400
        )
        _old_time = time.time
        time.time = lambda: expired_timestamp

        try:
            signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
            activation_key = signer.sign(self.valid_data['username'])
        finally:
            time.time = _old_time

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': activation_key}
            )
        )

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')

    def test_nonexistent_activation(self):
        """
        A nonexistent username in an activation key will fail to
        activate.

        """
        signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
        activation_key = signer.sign('parrot')

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': activation_key}
            )
        )

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')
