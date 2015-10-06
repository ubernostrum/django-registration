"""
Tests for the model-based activation workflow.

"""

import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import override_settings

from registration.models import RegistrationProfile

from .base import ActivationTestCase


@override_settings(ROOT_URLCONF='registration.backends.model_activation.urls')
class ModelActivationViewTests(ActivationTestCase):
    """
    Tests for the model-based activation workflow.

    """
    def test_activation(self):
        """
        Activation of an account functions properly.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        profile = RegistrationProfile.objects.get(
            user__username=self.valid_data['username']
        )

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': profile.activation_key}
            )
        )
        self.assertRedirects(resp, reverse('registration_activation_complete'))

    def test_activation_expired(self):
        """
        An expired account can't be activated.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        profile = RegistrationProfile.objects.get(
            user__username=self.valid_data['username']
        )
        user = profile.user
        user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1
        )
        user.save()

        resp = self.client.get(
            reverse(
                'registration_activate',
                args=(),
                kwargs={'activation_key': profile.activation_key}
            )
        )

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')


class ModelActivationCompatibilityTests(ModelActivationViewTests):
    """
    Re-run the model-activation workflow tests, but using the
    'registration.backends.default' import compatibility support, to
    ensure that it works.

    """
    def test_view_imports(self):
        """
        Importing the views from the old location works, and returns
        the correct view classes.

        """
        from registration.backends.default import views as old_views
        from registration.backends.model_activation import views as new_views

        self.assertEqual(
            old_views.ActivationView.__class__,
            new_views.ActivationView.__class__
        )

        self.assertEqual(
            old_views.RegistrationView.__class__,
            new_views.RegistrationView.__class__
        )
