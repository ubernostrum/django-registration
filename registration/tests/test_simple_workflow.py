"""
Tests for the simple one-step registration workflow.

"""

from django.core.urlresolvers import reverse
from django.test import modify_settings, override_settings

from .. import signals
from .base import WorkflowTestCase


@modify_settings(INSTALLED_APPS={'remove': 'registration'})
@override_settings(ROOT_URLCONF='registration.backends.simple.urls')
class SimpleWorkflowViewTests(WorkflowTestCase):
    """
    Tests for the simple one-step workflow.

    """
    def test_registration(self):
        """
        Registration creates a new account and logs the user in.

        """
        with self.assertSignalSent(signals.user_registered,
                                   required_kwargs=['user', 'request']) as cm:
            resp = self.client.post(
                reverse('registration_register'),
                data=self.valid_data
            )
            self.assertEqual(
                getattr(cm.received_kwargs['user'],
                        self.user_model.USERNAME_FIELD),
                self.valid_data[self.user_model.USERNAME_FIELD]
            )

        # fetch_redirect_response=False because the URLConf we're
        # using in these tests does not define a URL pattern for '/',
        # so allowing the default behavior would fail the test when
        # that URL 404s.
        self.assertRedirects(resp, '/', fetch_redirect_response=False)

        new_user = self.user_model.objects.get(**self.user_lookup_kwargs)
        self.assertTrue(
            new_user.check_password(
                self.valid_data['password1']
            )
        )
        self.assertEqual(new_user.email, self.valid_data['email'])

        # New user must be active.
        self.assertTrue(new_user.is_active)

        # New user must be logged in.
        resp = self.client.get(reverse('registration_register'))
        self.assertTrue(resp.context['user'].is_authenticated())
