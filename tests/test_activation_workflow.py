"""
Tests for the signed-token activation registration workflow.

"""

# SPDX-License-Identifier: BSD-3-Clause

import datetime
import time
from http import HTTPStatus

from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.http import HttpRequest
from django.test import modify_settings, override_settings
from django.urls import reverse

from django_registration import signals
from django_registration.backends.activation.forms import ActivationForm
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

    def test_activation_success_url(self):
        """
        Valid activation redirects to the success URL.

        """
        user_model = get_user_model()
        self.client.post(reverse("django_registration_register"), data=self.valid_data)
        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        activation_response = self.client.post(
            reverse("django_registration_activate"),
            data={"activation_key": activation_key},
        )
        self.assertRedirects(
            activation_response, reverse("django_registration_activation_complete")
        )

    def test_activation_success_signal(self):
        """
        Valid activation emits the user-activated signal.

        """
        user_model = get_user_model()
        self.client.post(reverse("django_registration_register"), data=self.valid_data)
        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        with self.assertSignalSent(signals.user_activated):
            self.client.post(
                reverse("django_registration_activate"),
                data={"activation_key": activation_key},
            )

    def test_activation_success_sets_is_active(self):
        """
        Valid activation marks the account as active.

        """
        user_model = get_user_model()
        self.client.post(reverse("django_registration_register"), data=self.valid_data)
        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )
        self.client.post(
            reverse("django_registration_activate"),
            data={"activation_key": activation_key},
        )

        user_account = user_model.objects.get(**self.user_lookup_kwargs)
        assert user_account.is_active

    def test_no_activation_on_get(self):
        """
        Account activation only occurs on HTTP POST, not GET.

        """
        user_model = get_user_model()

        resp = self.client.post(
            reverse("django_registration_register"), data=self.valid_data
        )

        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        with self.assertSignalNotSent(signals.user_activated):
            resp = self.client.get(
                reverse("django_registration_activate"),
                data={"activation_key": activation_key},
            )
            assert resp.status_code == HTTPStatus.OK

        user_account = user_model.objects.get(**self.user_lookup_kwargs)
        assert not user_account.is_active

    def test_form_populated(self):
        """
        HTTP GET with the activation key in the querystring populates the activation
        form.

        """
        user_model = get_user_model()

        resp = self.client.post(
            reverse("django_registration_register"), data=self.valid_data
        )

        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        resp = self.client.get(
            reverse("django_registration_activate"),
            data={"activation_key": activation_key},
        )
        assert resp.context["form"].initial["activation_key"] == activation_key

    def test_form_not_populated(self):
        """
        HTTP GET without the activation key in the querystring does not populate the
        activation form.

        """
        resp = self.client.post(
            reverse("django_registration_register"), data=self.valid_data
        )

        resp = self.client.get(
            reverse("django_registration_activate"),
        )
        assert resp.context["form"].initial == {}

    def test_repeat_activation(self):
        """
        Once activated, attempting to re-activate an account (even with a valid key)
        does nothing.

        """
        user_model = get_user_model()

        resp = self.client.post(
            reverse("django_registration_register"), data=self.valid_data
        )

        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        with self.assertSignalSent(signals.user_activated):
            resp = self.client.post(
                reverse("django_registration_activate"),
                data={"activation_key": activation_key},
            )
        # First activation redirects to success.
        self.assertRedirects(resp, reverse("django_registration_activation_complete"))

        with self.assertSignalNotSent(signals.user_activated):
            resp = self.client.post(
                reverse("django_registration_activate"),
                data={"activation_key": activation_key},
            )

        # Second activation fails.
        assert resp.status_code == HTTPStatus.OK
        assert resp.context["activation_error"] == {
            "message": ActivationView.ALREADY_ACTIVATED_MESSAGE,
            "code": "already_activated",
            "params": None,
        }

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
            resp = self.client.post(
                reverse("django_registration_activate"),
                data={"activation_key": activation_key},
            )

        assert resp.status_code == HTTPStatus.OK
        self.assertFormError(
            form=resp.context["form"],
            field="activation_key",
            errors=ActivationForm.INVALID_KEY_MESSAGE,
        )

    # The timestamp calculation will error if USE_TZ=True, due to trying to subtract a
    # naive from an aware datetime. Since time zones aren't relevant to the test, we
    # just temporarily disable time-zone support rather than do the more complex dance
    # of checking the setting and forcing everything to naive or aware.
    @override_settings(USE_TZ=False)
    def test_activation_expired(self):
        """
        An expired account can't be activated.

        """
        user_model = get_user_model()

        self.client.post(reverse("django_registration_register"), data=self.valid_data)

        # We need to create an activation key valid for the username, but with a
        # timestamp > ACCOUNT_ACTIVATION_DAYS days in the past. This requires
        # monkeypatching time.time() to return that timestamp, since TimestampSigner
        # uses time.time().
        #
        # On Python 3.3+ this is much easier because of the timestamp() method of
        # datetime objects, but since django-registration has to run on Python 2.7, we
        # manually calculate it using a timedelta between the signup date and the UNIX
        # epoch, and patch time.time() temporarily to return a date
        # (ACCOUNT_ACTIVATION_DAYS + 1) days in the past.
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
            resp = self.client.post(
                reverse("django_registration_activate"),
                data={"activation_key": activation_key},
            )

        assert resp.status_code == HTTPStatus.OK
        self.assertFormError(
            form=resp.context["form"],
            field="activation_key",
            errors=ActivationForm.EXPIRED_MESSAGE,
        )

    def test_nonexistent_activation(self):
        """
        A nonexistent username in an activation key will fail to activate.

        """
        activation_key = signing.dumps(obj="parrot", salt=REGISTRATION_SALT)

        with self.assertSignalNotSent(signals.user_activated):
            resp = self.client.post(
                reverse("django_registration_activate"),
                data={"activation_key": activation_key},
            )

        assert resp.status_code == HTTPStatus.OK
        assert "activation_error" in resp.context
        assert resp.context["activation_error"] == {
            "message": ActivationView.BAD_USERNAME_MESSAGE,
            "code": "bad_username",
            "params": None,
        }

    def test_activation_signal(self):
        """
        Activating a user account sends the activation signal.

        """
        user_model = get_user_model()

        self.client.post(reverse("django_registration_register"), data=self.valid_data)

        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        with self.assertSignalSent(
            signals.user_activated, required_kwargs=["user", "request"]
        ) as signal_context:
            self.client.post(
                reverse("django_registration_activate"),
                data={"activation_key": activation_key},
            )
            assert (
                signal_context.received_kwargs["user"].get_username()
                == self.valid_data[user_model.USERNAME_FIELD]
            )
            assert isinstance(signal_context.received_kwargs["request"], HttpRequest)


@override_settings(AUTH_USER_MODEL="tests.CustomUser")
@override_settings(ROOT_URLCONF="tests.urls.custom_user_activation")
class ActivationBackendCustomUserTests(ActivationBackendViewTests):
    """
    Runs the activation workflow's test suite, but with a custom user model.

    """

    def test_custom_user_configured(self):
        """
        Asserts that the user model in use is the custom user model defined in this
        test suite.

        """
        user_model = get_user_model()
        custom_user = apps.get_model("tests", "CustomUser")
        assert user_model is custom_user
