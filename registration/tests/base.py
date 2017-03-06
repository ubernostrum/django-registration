"""
Base classes for other test cases to inherit from.

"""
from contextlib import contextmanager

from django.contrib.auth import get_user_model
from django.core import mail
from django.http import HttpRequest
from django.test import TestCase, override_settings

from ..forms import RegistrationForm
from .. import signals

try:
    from django.urls import reverse
except ImportError:  # pragma: no cover
    from django.core.urlresolvers import reverse  # pragma: no cover


User = get_user_model()


# django-registration needs to test that signals are sent at
# registration and activation. Django -- as of 1.10 -- does not have a
# test assertion built in to test whether a signal was or was not
# sent. The code below is from a pull request submitted upstream to
# Django to add assertSignalSent and assertSignalNotSent assertions to
# Django's base test case class, and will be removed once it's been
# integrated into Django and django-registration is only supporting
# versions of Django which include it.
class _AssertSignalSentContext(object):
    def __init__(self, test_case, signal, required_kwargs=None):
        self.test_case = test_case
        self.signal = signal
        self.required_kwargs = required_kwargs

    def _listener(self, sender, **kwargs):
        self.signal_sent = True
        self.received_kwargs = kwargs
        self.sender = sender

    def __enter__(self):
        self.signal_sent = False
        self.received_kwargs = {}
        self.sender = None
        self.signal.connect(self._listener)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.signal.disconnect(self._listener)
        if not self.signal_sent:
            self.test_case.fail('Signal was not sent.')
            return
        if self.required_kwargs is not None:
            missing_kwargs = []
            for k in self.required_kwargs:
                if k not in self.received_kwargs:
                    missing_kwargs.append(k)
            if missing_kwargs:
                self.test_case.fail(
                    "Signal missing required arguments: "
                    "%s" % ','.join(missing_kwargs)
                )


class _AssertSignalNotSentContext(_AssertSignalSentContext):
    def __exit__(self, exc_type, exc_value, traceback):
        self.signal.disconnect(self._listener)
        if self.signal_sent:
            self.test_case.fail('Signal was unexpectedly sent.')


@override_settings(
    ACCOUNT_ACTIVATION_DAYS=7,
    REGISTRATION_OPEN=True
)
class RegistrationTestCase(TestCase):
    """
    Base class for test cases, defining valid data for registering a
    user account and looking up the account after creation.

    """
    user_model = User

    valid_data = {
        User.USERNAME_FIELD: 'alice',
        'email': 'alice@example.com',
        'password1': 'swordfish',
        'password2': 'swordfish',
    }

    user_lookup_kwargs = {
        User.USERNAME_FIELD: 'alice',
    }

    @contextmanager
    def assertSignalSent(self, signal, required_kwargs=None):
        with _AssertSignalSentContext(self, signal, required_kwargs) as cm:
            yield cm

    @contextmanager
    def assertSignalNotSent(self, signal):
        with _AssertSignalNotSentContext(self, signal) as cm:
            yield cm


class WorkflowTestCase(RegistrationTestCase):
    """
    Base class for the test cases which exercise the built-in
    workflows, including logic common to all of them (and which needs
    to be tested for each one).

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
        resp = self.client.get(
            reverse('registration_register')
        )
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
        self.assertTrue(
            isinstance(
                resp.context['form'], RegistrationForm
            )
        )

    def test_registration(self):
        """
        Registration creates a new account.

        """
        with self.assertSignalSent(signals.user_registered):
            resp = self.client.post(
                reverse('registration_register'),
                data=self.valid_data
            )

        self.assertRedirects(resp, reverse('registration_complete'))

        new_user = self.user_model.objects.get(**self.user_lookup_kwargs)

        self.assertTrue(
            new_user.check_password(
                self.valid_data['password1']
            )
        )
        self.assertEqual(new_user.email, self.valid_data['email'])

    def test_registration_failure(self):
        """
        Registering with invalid data fails.

        """
        data = self.valid_data.copy()
        data.update(password2='notsecret')

        with self.assertSignalNotSent(signals.user_registered):
            resp = self.client.post(
                reverse('registration_register'),
                data=data
            )

        self.assertEqual(200, resp.status_code)
        self.assertFalse(resp.context['form'].is_valid())
        self.assertTrue(resp.context['form'].has_error('password2'))

    def test_registration_signal(self):
        with self.assertSignalSent(signals.user_registered) as cm:
            self.client.post(
                reverse('registration_register'),
                data=self.valid_data
            )
            self.assertEqual(
                getattr(cm.received_kwargs['user'],
                        self.user_model.USERNAME_FIELD),
                self.valid_data[User.USERNAME_FIELD]
            )
            self.assertTrue(
                isinstance(cm.received_kwargs['request'], HttpRequest)
            )


class ActivationTestCase(WorkflowTestCase):
    """
    Base class for testing the built-in workflows which involve an
    activation step.

    """
    # First few methods repeat parent class, but with added checks for
    # is_active status and sending of activation emails.
    def test_registration(self):
        """
        Registration creates a new inactive account and sends an
        activation email.

        """
        with self.assertSignalSent(signals.user_registered):
            super(ActivationTestCase, self).test_registration()

        new_user = self.user_model.objects.get(**self.user_lookup_kwargs)

        # New user must not be active.
        self.assertFalse(new_user.is_active)

        # An activation email was sent.
        self.assertEqual(len(mail.outbox), 1)

    def test_registration_failure(self):
        """
        Registering with invalid data fails.

        """
        with self.assertSignalNotSent(signals.user_registered):
            super(ActivationTestCase, self).test_registration_failure()

        # Activation email was not sent.
        self.assertEqual(0, len(mail.outbox))

    def test_registration_no_sites(self):
        """
        Registration still functions properly when
        ``django.contrib.sites`` is not installed; the fallback will
        be a ``RequestSite`` instance.

        """
        with self.modify_settings(INSTALLED_APPS={
            'remove': ['django.contrib.sites']
        }):
            with self.assertSignalSent(signals.user_registered):
                resp = self.client.post(
                    reverse('registration_register'),
                    data=self.valid_data
                )

            self.assertEqual(302, resp.status_code)

            new_user = self.user_model.objects.get(**self.user_lookup_kwargs)

            self.assertTrue(
                new_user.check_password(
                    self.valid_data['password1']
                )
            )
            self.assertEqual(new_user.email, self.valid_data['email'])
