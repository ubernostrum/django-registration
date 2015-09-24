"""
Tests for the simple one-step registration workflow.

"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

from registration.forms import RegistrationForm


@override_settings(
    ROOT_URLCONF='registration.backends.simple.urls',
    REGISTRATION_OPEN=True
)
class SimpleWorkflowViewTests(TestCase):
    """
    Tests for the simple one-step workflow.

    """
    valid_data = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password1': 'secret',
        'password2': 'secret'
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
        resp = self.client.get(reverse('registration_register'))
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
        self.assertTrue(isinstance(resp.context['form'],
                        RegistrationForm))

    def test_registration(self):
        """
        Registration creates a new account and logs the user in.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data=self.valid_data
        )

        new_user = User.objects.get(username=self.valid_data['username'])
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
