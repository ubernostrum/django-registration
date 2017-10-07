"""
Tests for django-registration's built-in views.

"""

from django.test import override_settings

from ..models import RegistrationProfile
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
        self.assertRedirects(resp, '/activate/complete/')

    def test_registration_redirect(self):
        """
        ``redirect_authenticated_user``, when ``True``, redirects
        authenticated users to success_url.

        """
        self.client.login(**{
            self.user_model.USERNAME_FIELD: self.valid_data[self.user_model.USERNAME_FIELD],
            'password': self.valid_data['password1'],
        })
        resp = self.client.get(reverse('registration_register_or_redirect'))
        self.assertRedirects(resp, '/')
