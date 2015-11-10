"""
Tests for the HMAC signed-token registration workflow.

"""

import datetime
import time

from django.conf import settings
from django.core import signing
from django.core.urlresolvers import reverse
from django.test import override_settings

from registration.backends.hmac.views import REGISTRATION_SALT

from .base import ActivationTestCase


@override_settings(ROOT_URLCONF='registration.backends.hmac.urls')
class HMACViewTests(ActivationTestCase):
    """
    Tests for the signed-token registration workflow.

    """
    def test_activation(self):
        """
        Activation of an account functions properly.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        activation_key = signing.dumps(
            obj=self.valid_data['username'],
            salt=REGISTRATION_SALT
        )

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

        activation_key = signing.dumps(
            obj=self.valid_data['username'],
            salt=REGISTRATION_SALT
        )

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
        user = self.user_model.objects.get(**self.user_lookup_kwargs)
        joined_timestamp = (
            user.date_joined - datetime.datetime.fromtimestamp(0)
        ).total_seconds()
        expired_timestamp = (
            joined_timestamp - (settings.ACCOUNT_ACTIVATION_DAYS + 1) * 86400
        )
        _old_time = time.time
        time.time = lambda: expired_timestamp

        try:
            activation_key = signing.dumps(
                obj=self.valid_data['username'],
                salt=REGISTRATION_SALT
            )
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
        activation_key = signing.dumps(
            obj='parrot',
            salt=REGISTRATION_SALT
        )

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': activation_key}
            )
        )

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')
