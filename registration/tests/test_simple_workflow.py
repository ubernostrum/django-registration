"""
Tests for the simple one-step registration workflow.

"""

from django.core.urlresolvers import reverse
from django.test import override_settings

from .base import WorkflowTestCase


@override_settings(ROOT_URLCONF='registration.backends.simple.urls')
class SimpleWorkflowViewTests(WorkflowTestCase):
    """
    Tests for the simple one-step workflow.

    """
    def test_registration(self):
        """
        Registration creates a new account and logs the user in.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        new_user = self.user_model.objects.get(**self.user_lookup_kwargs)
        self.assertEqual(302, resp.status_code)
        self.assertEqual('http://testserver/', resp['Location'])

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
