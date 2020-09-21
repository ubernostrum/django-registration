"""
Tests for the signed-token activation registration workflow.

"""

import datetime
import time

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.http import HttpRequest
from django.test import modify_settings, override_settings
from django.urls import reverse

from django_registration import signals
from django_registration.backends.activation.views import (
    REGISTRATION_SALT,
    ActivationView,
)

from .base import ActivationTestCase


@modify_settings(INSTALLED_APPS={"remove": "django_registration"})
@override_settings(ROOT_URLCONF="django_registration.backends.activation.urls")
class ActivationBackendViewTests(ActivationTestCase):
    """
    Tests for the signed-token activation registration workflow.

    """

    def test_activation(self):
        """
        Activation of an account functions properly.

        """
        user_model = get_user_model()

        resp = self.client.post(
            reverse("django_registration_register"), data=self.valid_data
        )

        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        with self.assertSignalSent(signals.user_activated):
            resp = self.client.get(
                reverse(
                    "django_registration_activate",
                    args=(),
                    kwargs={"activation_key": activation_key},
                )
            )

        self.assertRedirects(resp, reverse("django_registration_activation_complete"))

    def test_repeat_activation(self):
        """
        Once activated, attempting to re-activate an account (even
        with a valid key) does nothing.

        """
        user_model = get_user_model()

        resp = self.client.post(
            reverse("django_registration_register"), data=self.valid_data
        )

        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        with self.assertSignalSent(signals.user_activated):
            resp = self.client.get(
                reverse(
                    "django_registration_activate",
                    args=(),
                    kwargs={"activation_key": activation_key},
                )
            )
        # First activation redirects to success.
        self.assertRedirects(resp, reverse("django_registration_activation_complete"))

        with self.assertSignalNotSent(signals.user_activated):
            resp = self.client.get(
                reverse(
                    "django_registration_activate",
                    args=(),
                    kwargs={"activation_key": activation_key},
                )
            )

        # Second activation fails.
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, "django_registration/activation_failed.html")
        self.assertEqual(
            resp.context["activation_error"],
            {
                "message": ActivationView.ALREADY_ACTIVATED_MESSAGE,
                "code": "already_activated",
                "params": None,
            },
        )

    def test_bad_key(self):
        """
        An invalid activation key fails to activate.

        """
        user_model = get_user_model()

        resp = self.client.post(
            reverse("django_registration_register"), data=self.valid_data
        )

        activation_key = self.valid_data[user_model.USERNAME_FIELD]
        with self.assertSignalNotSent(signals.user_activated):
            resp = self.client.get(
                reverse(
                    "django_registration_activate",
                    args=(),
                    kwargs={"activation_key": activation_key},
                )
            )

        # Second activation fails.
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, "django_registration/activation_failed.html")
        self.assertTrue("activation_error" in resp.context)
        self.assertEqual(
            resp.context["activation_error"],
            {
                "message": ActivationView.INVALID_KEY_MESSAGE,
                "code": "invalid_key",
                "params": {"activation_key": activation_key},
            },
        )

    # The timestamp calculation will error if USE_TZ=True, due to
    # trying to subtract a naive from an aware datetime. Since time
    # zones aren't relevant to the test, we just temporarily disable
    # time-zone support rather than do the more complex dance of
    # checking the setting and forcing everything to naive or aware.
    @override_settings(USE_TZ=False)
    def test_activation_expired(self):
        """
        An expired account can't be activated.

        """
        user_model = get_user_model()

        self.client.post(reverse("django_registration_register"), data=self.valid_data)

        # We need to create an activation key valid for the username,
        # but with a timestamp > ACCOUNT_ACTIVATION_DAYS days in the
        # past. This requires monkeypatching time.time() to return
        # that timestamp, since TimestampSigner uses time.time().
        #
        # On Python 3.3+ this is much easier because of the
        # timestamp() method of datetime objects, but since
        # django-registration has to run on Python 2.7, we manually
        # calculate it using a timedelta between the signup date and
        # the UNIX epoch, and patch time.time() temporarily to return
        # a date (ACCOUNT_ACTIVATION_DAYS + 1) days in the past.
        user = user_model.objects.get(**self.user_lookup_kwargs)
        joined_timestamp = (
            user.date_joined - datetime.datetime.fromtimestamp(0)
        ).total_seconds()
        expired_timestamp = (
            joined_timestamp - (settings.ACCOUNT_ACTIVATION_DAYS + 1) * 86400
        )
        _old_time = time.time

        try:
            time.time = lambda: expired_timestamp
            activation_key = signing.dumps(
                obj=self.valid_data[user_model.USERNAME_FIELD],
                salt=REGISTRATION_SALT,
            )
        finally:
            time.time = _old_time

        with self.assertSignalNotSent(signals.user_activated):
            resp = self.client.get(
                reverse(
                    "django_registration_activate",
                    args=(),
                    kwargs={"activation_key": activation_key},
                )
            )

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, "django_registration/activation_failed.html")
        self.assertTrue("activation_error" in resp.context)
        self.assertEqual(
            resp.context["activation_error"],
            {
                "message": ActivationView.EXPIRED_MESSAGE,
                "code": "expired",
                "params": None,
            },
        )

    def test_nonexistent_activation(self):
        """
        A nonexistent username in an activation key will fail to
        activate.

        """
        activation_key = signing.dumps(obj="parrot", salt=REGISTRATION_SALT)

        with self.assertSignalNotSent(signals.user_activated):
            resp = self.client.get(
                reverse(
                    "django_registration_activate",
                    args=(),
                    kwargs={"activation_key": activation_key},
                )
            )

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, "django_registration/activation_failed.html")
        self.assertTrue("activation_error" in resp.context)
        self.assertEqual(
            resp.context["activation_error"],
            {
                "message": ActivationView.BAD_USERNAME_MESSAGE,
                "code": "bad_username",
                "params": None,
            },
        )

    def test_activation_signal(self):
        user_model = get_user_model()

        self.client.post(reverse("django_registration_register"), data=self.valid_data)

        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        with self.assertSignalSent(
            signals.user_activated, required_kwargs=["user", "request"]
        ) as cm:
            self.client.get(
                reverse(
                    "django_registration_activate",
                    args=(),
                    kwargs={"activation_key": activation_key},
                )
            )
            self.assertEqual(
                cm.received_kwargs["user"].get_username(),
                self.valid_data[user_model.USERNAME_FIELD],
            )
            self.assertTrue(isinstance(cm.received_kwargs["request"], HttpRequest))


@override_settings(AUTH_USER_MODEL="tests.CustomUser")
@override_settings(ROOT_URLCONF="tests.urls.custom_user_activation")
class ActivationBackendCustomUserTests(ActivationBackendViewTests):
    """
    Runs the activation workflow's test suite, but with a custom user model.

    """

    def test_custom_user_configured(self):
        """
        Asserts that the user model in use is the custom user model
        defined in this test suite.

        """
        user_model = get_user_model()
        custom_user = apps.get_model("tests", "CustomUser")
        assert user_model is custom_user
