"""
Tests for django-registration's built-in views.

"""

from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.urls import reverse

from django_registration.backends.activation.views import REGISTRATION_SALT
from django_registration.views import RegistrationView

from .base import RegistrationTestCase


@override_settings(ROOT_URLCONF="tests.urls.view_tests")
class ActivationViewTests(RegistrationTestCase):
    """
    Tests for aspects of the activation view not currently exercised
    by any built-in workflow.

    """

    @override_settings(ACCOUNT_ACTIVATION_DAYS=7)
    def test_activation(self):
        """
        Activation of an account functions properly when using a
        string URL as the success redirect.

        """
        user_model = get_user_model()
        resp = self.client.post(
            reverse("django_registration_register"), data=self.valid_data
        )

        activation_key = signing.dumps(
            obj=self.valid_data[user_model.USERNAME_FIELD], salt=REGISTRATION_SALT
        )

        resp = self.client.get(
            reverse(
                "django_registration_activate",
                args=(),
                kwargs={"activation_key": activation_key},
            )
        )
        self.assertRedirects(resp, "/activate/complete/")


@override_settings(AUTH_USER_MODEL="tests.CustomUser")
class CustomUserTests(RegistrationTestCase):
    """
    Test custom-user support.

    """

    def test_user_mismatch_breaks_view(self):
        """
        When RegistrationView detects a mismatch between the model used by
        its form class and the configured user model, it raises
        ImproperlyConfigured.

        """
        view = RegistrationView()
        with self.assertRaises(ImproperlyConfigured):
            view.get_form()
