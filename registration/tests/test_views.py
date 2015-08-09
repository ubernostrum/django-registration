from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import override_settings, TestCase

from ..models import RegistrationProfile


class ActivationViewTests(TestCase):
    urls = 'registration.tests.urls'
    
    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_activation(self):
        """
        Activation of an account functions properly when using a
        simple string URL as the success redirect.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        profile = RegistrationProfile.objects.get(user__username='bob')

        resp = self.client.get(reverse(
            'registration_activate',
            args=(),
            kwargs={'activation_key': profile.activation_key})
        )
        self.assertRedirects(resp, '/')

