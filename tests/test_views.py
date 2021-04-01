"""
Tests for django-registration's built-in views.

"""

import logging
import sys

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core import mail, signing
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, override_settings
from django.urls import reverse

from django_registration import forms
from django_registration import views as base_views
from django_registration.backends.activation import views as activation_views
from django_registration.backends.one_step import views as one_step_views

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
            obj=self.valid_data[user_model.USERNAME_FIELD],
            salt=activation_views.REGISTRATION_SALT,
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
        for view_class in (
            base_views.RegistrationView,
            activation_views.RegistrationView,
            one_step_views.RegistrationView,
        ):
            for form_class in (
                forms.RegistrationForm,
                forms.RegistrationFormCaseInsensitive,
                forms.RegistrationFormTermsOfService,
                forms.RegistrationFormUniqueEmail,
            ):
                view = view_class()
                message = base_views.USER_MODEL_MISMATCH.format(
                    view=view.__class__,
                    form=forms.RegistrationForm,
                    form_model=form_class._meta.model,
                    user_model=get_user_model(),
                )
                with self.assertRaisesMessage(ImproperlyConfigured, message):
                    view.get_form()


class RegistrationError(Exception):
    """
    Distinct exception class to simulate an unhandled error in the below
    tests.

    """


class BuggyRegistrationView(base_views.RegistrationView):
    """
    Registration view that simulates an unhandled exception.

    """

    def registration_allowed(self):
        raise RegistrationError("catch me if you can")


buggy_view = BuggyRegistrationView.as_view()


@override_settings(ADMINS=[("Admin", "admin@localhost")])
class SensitiveParameterFilterTests(RegistrationTestCase):
    """
    Test filtering of sensitive POST parameters in error reports for the
    registration view.

    """

    logger = logging.getLogger("django")
    factory = RequestFactory()

    def test_sensitive_post_parameters_are_filtered(self):
        """
        When an unexpected exception occurs during a POST request to the
        registration view, the default email report to ADMINS must not
        contain the submitted passwords.

        """
        request = self.factory.post("/raise/", data=self.valid_data)
        request.user = AnonymousUser()
        # we cannot use self.assertRaises(...) here because of sys.exc_info()
        try:
            buggy_view(request)
            self.fail("expected exception not thrown")
        except RegistrationError as error:
            self.assertEqual(str(error), "catch me if you can")
            # based on code in Django (tests/view_tests/views.py)
            self.logger.error(
                "Internal Server Error: %s" % request.path,
                exc_info=sys.exc_info(),
                extra={"status_code": 500, "request": request},
            )
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn("RegistrationError at /raise/", email.body)
        self.assertIn("catch me if you can", email.body)
        self.assertIn("No GET data", email.body)
        self.assertNotIn("No POST data", email.body)
        self.assertIn("password1", email.body)
        self.assertIn("password2", email.body)
        self.assertNotIn(self.valid_data["password1"], email.body)
        self.assertNotIn(self.valid_data["password2"], email.body)
        self.assertNotIn(self.valid_data["email"], email.body)
