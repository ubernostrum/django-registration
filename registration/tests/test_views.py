"""
Tests for django-registration's built-in views.

"""

from django.core import signing
from django.test import override_settings

from registration.backends.hmac.views import REGISTRATION_SALT

from .base import RegistrationTestCase

try:
    from django.urls import reverse
except ImportError:  # pragma: no cover
    from django.core.urlresolvers import reverse  # pragma: no cover


@override_settings(ROOT_URLCONF='registration.tests.urls')
class ActivationViewTests(RegistrationTestCase):
    """
    Tests for aspects of the activation view not currently exercised
    by any built-in workflow.

    """
    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_activation(self):
        """
        Activation of an account functions properly when using a
        string URL as the success redirect.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        activation_key = signing.dumps(
            obj=self.valid_data[self.user_model.USERNAME_FIELD],
            salt=REGISTRATION_SALT
        )

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': activation_key}
            )
        )
        self.assertRedirects(resp, '/activate/complete/')
