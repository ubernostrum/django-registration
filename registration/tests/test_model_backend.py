"""
Tests for the model-based activation workflow.

"""

import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import override_settings, TestCase

from registration.forms import RegistrationForm
from registration.models import RegistrationProfile


@override_settings(
    ROOT_URLCONF='registration.backends.model_activation.urls',
    ACCOUNT_ACTIVATION_DAYS=7,
    REGISTRATION_OPEN=True
)
class ModelActivationViewTests(TestCase):
    """
    Tests for the model-based activation workflow.

    """
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
            data={'username': 'bob',
                  'email': 'bob@example.com',
                  'password1': 'secret',
                  'password2': 'secret'}
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
        self.assertTrue(
            isinstance(
                resp.context['form'],
                RegistrationForm
            )
        )

    def test_registration(self):
        """
        Registration creates a new inactive account and a new profile
        with activation key, populates the correct account data and
        sends an activation email.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data={'username': 'bob',
                  'email': 'bob@example.com',
                  'password1': 'secret',
                  'password2': 'secret'}
        )
        self.assertRedirects(resp, reverse('registration_complete'))

        new_user = User.objects.get(username='bob')

        self.assertTrue(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        # New user must not be active.
        self.assertFalse(new_user.is_active)

        # A registration profile was created, and an activation email
        # was sent.
        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_registration_no_sites(self):
        """
        Registration still functions properly when
        ``django.contrib.sites`` is not installed; the fallback will
        be a ``RequestSite`` instance.

        """
        with self.modify_settings(INSTALLED_APPS={
            'remove': [
                'django.contrib.sites'
            ]
        }):
            resp = self.client.post(
                reverse('registration_register'),
                data={'username': 'bob',
                      'email': 'bob@example.com',
                      'password1': 'secret',
                      'password2': 'secret'}
            )
            self.assertEqual(302, resp.status_code)

            new_user = User.objects.get(username='bob')

            self.assertTrue(new_user.check_password('secret'))
            self.assertEqual(new_user.email, 'bob@example.com')

            self.assertFalse(new_user.is_active)

            self.assertEqual(1, RegistrationProfile.objects.count())
            self.assertEqual(len(mail.outbox), 1)

    def test_registration_failure(self):
        """
        Registering with invalid data fails.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data={'username': 'bob',
                  'email': 'bob@example.com',
                  'password1': 'secret',
                  'password2': 'notsecret'}
        )
        self.assertEqual(200, resp.status_code)
        self.assertFalse(resp.context['form'].is_valid())
        self.assertEqual(0, len(mail.outbox))

    def test_activation(self):
        """
        Activation of an account functions properly.

        """
        resp = self.client.post(
            reverse('registration_register'),
            data={'username': 'bob',
                  'email': 'bob@example.com',
                  'password1': 'secret',
                  'password2': 'secret'}
        )

        profile = RegistrationProfile.objects.get(user__username='bob')

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
            data={'username': 'bob',
                  'email': 'bob@example.com',
                  'password1': 'secret',
                  'password2': 'secret'}
        )

        profile = RegistrationProfile.objects.get(user__username='bob')
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


@override_settings(
    ROOT_URLCONF='registration.backends.default.urls',
    ACCOUNT_ACTIVATION_DAYS=7,
    REGISTRATION_OPEN=True
)
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
