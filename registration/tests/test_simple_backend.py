from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import override_settings, TestCase

from registration.forms import RegistrationForm


@override_settings(ROOT_URLCONF='registration.backends.simple.urls',
                   REGISTRATION_OPEN=True)
class SimpleBackendViewTests(TestCase):
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

        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        self.assertRedirects(resp, reverse('registration_disallowed'))

    def test_registration_get(self):
        """
        HTTP ``GET`` to the registration view uses the appropriate
        template and populates a registration form into the context.

        """
        resp = self.client.get(reverse('registration_register'))
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp,
                                'registration/registration_form.html')
        self.assertTrue(isinstance(resp.context['form'],
                        RegistrationForm))

    def test_registration(self):
        """
        Registration creates a new account and logs the user in.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        new_user = User.objects.get(username='bob')
        self.assertEqual(302, resp.status_code)
        self.assertEqual('http://testserver/', resp['Location'])

        self.assertTrue(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        # New user must be active.
        self.assertTrue(new_user.is_active)

        # New user must be logged in.
        resp = self.client.get(reverse('registration_register'))
        self.assertTrue(resp.context['user'].is_authenticated())

    def test_registration_failure(self):
        """
        Registering with invalid data fails.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'notsecret'})
        self.assertEqual(200, resp.status_code)
        self.assertFalse(resp.context['form'].is_valid())
