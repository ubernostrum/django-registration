"""
Tests for django-registration's built-in views.

"""

from django.core.urlresolvers import reverse
from django.test import override_settings

from ..models import RegistrationProfile
from .base import RegistrationTestCase


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
        simple string URL as the success redirect.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        profile = RegistrationProfile.objects.get(
            user__username=self.valid_data[self.user_model.USERNAME_FIELD]
        )

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': profile.activation_key}
            )
        )
        self.assertRedirects(resp, '/')
