# -*- coding: utf-8 -*-
"""
Exercise django-registration's built-in form classes.

"""
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import modify_settings

from django_registration import forms, validators

from .base import RegistrationTestCase


@modify_settings(INSTALLED_APPS={"remove": "registration"})
class RegistrationFormTests(RegistrationTestCase):
    """
    Test the built-in form classes.

    """

    def test_email_required(self):
        """
        The email address field is required.

        """
        form = forms.RegistrationForm()
        self.assertTrue(form.fields["email"].required)

    def test_email_validation(self):
        """
        Stricter-than-RFC email validation is applied.

        This test is necessary because of the combination of
        HTML5EmailValidator and validate_confusables_email() in the
        default validator set for the email field of RegistrationForm;
        some technically-valid email addresses which nonetheless
        usually indicate bad faith or at least mischief are to be
        rejected before the confusables validator is applied.

        """
        user_model = get_user_model()

        for value in (
            "test@example.com",
            "test+test@example.com",
            "test.test@example.com",
            "test_test@example.com",
        ):
            user_data = self.valid_data.copy()
            user_data["email"] = value
            form = forms.RegistrationForm(data=user_data)
            self.assertTrue(form.is_valid())
        for value in (
            "@@@example.com",
            "test:test@test@example.com",
            'test"test@example"test@example.com',
        ):
            user_data = self.valid_data.copy()
            user_data["email"] = value
            form = forms.RegistrationForm(data=user_data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error(user_model.get_email_field_name()))
            self.assertTrue(
                str(validators.HTML5EmailValidator.message)
                in form.errors[user_model.get_email_field_name()]
            )

    def test_username_uniqueness(self):
        """
        Username uniqueness is enforced.

        This test is necessary as of 2.1.x to ensure the base
        UserCreationForm clean() continues to be called from the
        overridden clean() in RegistrationForm.

        """
        user_data = self.valid_data.copy()
        del user_data["password1"]
        del user_data["password2"]
        user_data["password"] = "swordfish"
        user_model = get_user_model()
        existing_user = user_model(**user_data)
        existing_user.save()
        form = forms.RegistrationForm(data=self.valid_data.copy())
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error(user_model.USERNAME_FIELD))

    def test_reserved_names(self):
        """
        Reserved names are disallowed.

        """
        user_model = get_user_model()
        for reserved_name in validators.DEFAULT_RESERVED_NAMES:
            data = self.valid_data.copy()
            data[user_model.USERNAME_FIELD] = reserved_name
            form = forms.RegistrationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error(user_model.USERNAME_FIELD))
            self.assertTrue(
                str(validators.RESERVED_NAME) in form.errors[user_model.USERNAME_FIELD]
            )

    def test_confusable_usernames(self):
        """
        Usernames containing dangerously confusable use of Unicode are
        disallowed.

        """
        user_model = get_user_model()
        for dangerous_value in (
            "p\u0430yp\u0430l",
            "g\u043e\u043egle",
            "\u03c1ay\u03c1al",
        ):
            data = self.valid_data.copy()
            data[user_model.USERNAME_FIELD] = dangerous_value
            form = forms.RegistrationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error(user_model.USERNAME_FIELD))
            self.assertTrue(
                str(validators.CONFUSABLE) in form.errors[user_model.USERNAME_FIELD]
            )

    def test_confusable_emails(self):
        """
        Usernames containing dangerously confusable use of Unicode are
        disallowed.

        """
        for dangerous_value in (
            "p\u0430yp\u0430l@example.com",
            "g\u043e\u043egle@example.com",
            "\u03c1y\u03c1al@example.com",
            "paypal@ex\u0430mple.com",
            "google@exam\u03c1le.com",
        ):
            data = self.valid_data.copy()
            data["email"] = dangerous_value
            form = forms.RegistrationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error("email"))
            self.assertTrue(str(validators.CONFUSABLE_EMAIL) in form.errors["email"])

    def test_custom_reserved_names(self):
        """
        Reserved names can be overridden by an attribute.

        """
        custom_reserved_names = ["foo", "bar", "eggs", "spam"]

        class CustomReservedNamesForm(forms.RegistrationForm):
            reserved_names = custom_reserved_names

        user_model = get_user_model()
        for reserved_name in custom_reserved_names:
            data = self.valid_data.copy()
            data[user_model.USERNAME_FIELD] = reserved_name
            form = CustomReservedNamesForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error(user_model.USERNAME_FIELD))
            self.assertTrue(
                str(validators.RESERVED_NAME) in form.errors[user_model.USERNAME_FIELD]
            )

    def test_reserved_name_non_string(self):
        """
        GitHub issue #82: reserved-name validator should not attempt
        to validate a non-string 'username'.

        """
        validator = validators.ReservedNameValidator()
        for value in (123456, 1.7, uuid.uuid4()):
            self.assertTrue(validator(value) is None)

    def test_reserved_name_validator_eq(self):
        """
        Test ReservedNameValidator __eq__ method.
        __eq__ is necessary for serializing custom user models that use
        the validator.

        """
        validator = validators.ReservedNameValidator()
        validator_same = validators.ReservedNameValidator()
        self.assertTrue(validator.__eq__(validator_same))

        validator_different = validators.ReservedNameValidator(reserved_names=[])
        self.assertFalse(validator.__eq__(validator_different))

    def test_email_validator(self):
        """
        Test the HTMl5 email address validator.

        """
        validator = validators.HTML5EmailValidator()
        for value in (
            "test@example.com",
            "test+test@example.com",
            "test.test@example.com",
            "test_test@example.com",
        ):
            self.assertTrue(validator(value) is None)
        for value in (
            "@@@example.com",
            "test:test@test@example.com",
            'test"test@example"test@example.com',
        ):
            with self.assertRaisesMessage(ValidationError, str(validator.message)):
                validator(value)

    def test_case_insensitive_validator(self):
        """
        Test the case-insensitive username validator.

        """
        user_model = get_user_model()
        validator = validators.CaseInsensitiveUnique(
            user_model,
            user_model.USERNAME_FIELD,
            validators.DUPLICATE_USERNAME,
        )
        for value in (123456, 1.7, uuid.uuid4()):
            self.assertTrue(validator(value) is None)

        base_creation_data = self.valid_data.copy()
        base_creation_data["password"] = base_creation_data["password1"]
        del base_creation_data["password1"]
        del base_creation_data["password2"]

        test_names = [("alice", "ALICE"), ("ALICE", "alice"), ("Alice", "alice")]
        test_names.extend([("STRASSBURGER", "straßburger")])

        for name, conflict in test_names:
            creation_data = base_creation_data.copy()
            creation_data[user_model.USERNAME_FIELD] = name
            existing_user = user_model(**creation_data)
            existing_user.save()
            with self.assertRaisesMessage(
                ValidationError, str(validators.DUPLICATE_USERNAME)
            ):
                validator(conflict)
            existing_user.delete()

    def test_case_insensitive_validator_eq(self):
        """
        Test CaseInsensitiveUnique __eq__ method.
        __eq__ is necessary for serializing custom user models that use
        the validator.

        """
        user_model = get_user_model()
        validator = validators.CaseInsensitiveUnique(
            user_model,
            user_model.USERNAME_FIELD,
            validators.DUPLICATE_USERNAME,
        )
        validator_same = validators.CaseInsensitiveUnique(
            user_model,
            user_model.USERNAME_FIELD,
            validators.DUPLICATE_USERNAME,
        )
        self.assertTrue(validator.__eq__(validator_same))

        validator_different = validators.CaseInsensitiveUnique(
            user_model, "not username field", validators.DUPLICATE_USERNAME
        )
        self.assertFalse(validator.__eq__(validator_different))

    def test_case_insensitive_form(self):
        """
        Test the case-insensitive registration form.

        """
        base_creation_data = self.valid_data.copy()
        base_creation_data["password"] = base_creation_data["password1"]
        del base_creation_data["password1"]
        del base_creation_data["password2"]

        test_names = [
            ("alice", "ALICE"),
            ("ALICE", "alice"),
            ("Alice", "alice"),
            ("AlIcE", "aLiCe"),
            ("STRASSBURGER", "straßburger"),
        ]

        user_model = get_user_model()

        for name, conflict in test_names:
            creation_data = base_creation_data.copy()
            creation_data[user_model.USERNAME_FIELD] = name
            existing_user = user_model(**creation_data)
            existing_user.save()
            user_data = self.valid_data.copy()
            user_data[user_model.USERNAME_FIELD] = name
            form = forms.RegistrationFormCaseInsensitive(data=user_data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error(user_model.USERNAME_FIELD))
            self.assertEqual(
                [str(validators.DUPLICATE_USERNAME)],
                form.errors[user_model.USERNAME_FIELD],
            )
            self.assertEqual(1, len(form.errors[user_model.USERNAME_FIELD]))

    def test_tos_field(self):
        """
        The terms-of-service field on RegistrationFormTermsOfService
        is required.

        """
        form = forms.RegistrationFormTermsOfService(data=self.valid_data.copy())
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error("tos"))
        self.assertEqual(form.errors["tos"], [str(validators.TOS_REQUIRED)])

    def test_email_uniqueness(self):
        """
        Email uniqueness is enforced by RegistrationFormUniqueEmail.

        """
        user_model = get_user_model()
        user_model.objects.create(
            username="bob",
            email=self.valid_data["email"],
            password=self.valid_data["password1"],
        )

        form = forms.RegistrationFormUniqueEmail(data=self.valid_data.copy())
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error("email"))
        self.assertEqual(form.errors["email"], [str(validators.DUPLICATE_EMAIL)])

        data = self.valid_data.copy()
        data.update(email="bob@example.com")
        form = forms.RegistrationFormUniqueEmail(data=data)
        self.assertTrue(form.is_valid())

    def test_confusables_validator(self):
        """
        Test the confusable-username validator standalone.

        """
        for dangerous_value in (
            "p\u0430yp\u0430l",
            "g\u043e\u043egle",
            "\u03c1ay\u03c1al",
        ):
            with self.assertRaises(ValidationError):
                validators.validate_confusables(dangerous_value)
        for safe_value in (
            "paypal",
            "google",
            "root",
            "admin",
            "\u041f\u0451\u0442\u0440",
            "\u5c71\u672c",
            3,
        ):
            validators.validate_confusables(safe_value)

    def test_confusables_email_validator(self):
        """
        Test the confusable-email validator standalone.

        """
        for dangerous_value in (
            "p\u0430yp\u0430l@example.com",
            "g\u043e\u043egle@example.com",
            "\u03c1ay\u03c1al@example.com",
            "paypal@ex\u0430mple.com",
            "google@exam\u03c1le.com",
        ):
            with self.assertRaises(ValidationError):
                validators.validate_confusables_email(dangerous_value)
        for safe_value in (
            "paypal@example.com",
            "google@example.com",
            "\u041f\u0451\u0442\u0440@example.com",
            "\u5c71\u672c@example.com",
            "username",
        ):
            validators.validate_confusables_email(safe_value)
