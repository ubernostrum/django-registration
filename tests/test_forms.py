# -*- coding: utf-8 -*-
"""
Exercise django-registration's built-in form classes.

"""
import uuid

from django.core.exceptions import ValidationError
from django.test import modify_settings
from django.utils import six

from django_registration import forms, validators

from .base import RegistrationTestCase


@modify_settings(INSTALLED_APPS={'remove': 'registration'})
class RegistrationFormTests(RegistrationTestCase):
    """
    Test the built-in form classes.

    """
    def test_email_required(self):
        """
        The email address field is required.

        """
        form = forms.RegistrationForm()
        self.assertTrue(
            form.fields['email'].required
        )

    def test_username_uniqueness(self):
        """
        Username uniqueness is enforced.

        This test is necessary as of 2.1.x to ensure the base
        UserCreationForm clean() continues to be called from the
        overridden clean() in RegistrationForm.

        """
        user_data = self.valid_data.copy()
        del user_data['password1']
        del user_data['password2']
        user_data['password'] = 'swordfish'
        existing_user = self.user_model(**user_data)
        existing_user.save()
        form = forms.RegistrationForm(data=self.valid_data.copy())
        self.assertFalse(form.is_valid())
        self.assertTrue(
            form.has_error(self.user_model.USERNAME_FIELD)
        )

    def test_reserved_names(self):
        """
        Reserved names are disallowed.

        """
        for reserved_name in validators.DEFAULT_RESERVED_NAMES:
            data = self.valid_data.copy()
            data[self.user_model.USERNAME_FIELD] = reserved_name
            form = forms.RegistrationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertTrue(
                form.has_error(self.user_model.USERNAME_FIELD)
            )
            self.assertTrue(
                six.text_type(validators.RESERVED_NAME) in
                form.errors[self.user_model.USERNAME_FIELD]
            )

    def test_confusable_usernames(self):
        """
        Usernames containing dangerously confusable use of Unicode are
        disallowed.

        """
        for dangerous_value in (
                u'p\u0430yp\u0430l',
                u'g\u043e\u043egle',
                u'\u03c1ay\u03c1al',
        ):
            data = self.valid_data.copy()
            data[self.user_model.USERNAME_FIELD] = dangerous_value
            form = forms.RegistrationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertTrue(
                form.has_error(self.user_model.USERNAME_FIELD)
            )
            self.assertTrue(
                six.text_type(validators.CONFUSABLE) in
                form.errors[self.user_model.USERNAME_FIELD]
            )

    def test_confusable_emails(self):
        """
        Usernames containing dangerously confusable use of Unicode are
        disallowed.

        """
        for dangerous_value in (
                u'p\u0430yp\u0430l@example.com',
                u'g\u043e\u043egle@example.com',
                u'\u03c1y\u03c1al@example.com',
                u'paypal@ex\u0430mple.com',
                u'google@exam\u03c1le.com',
        ):
            data = self.valid_data.copy()
            data['email'] = dangerous_value
            form = forms.RegistrationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error('email'))
            self.assertTrue(
                six.text_type(validators.CONFUSABLE_EMAIL) in
                form.errors['email']
            )

    def test_custom_reserved_names(self):
        """
        Reserved names can be overridden by an attribute.

        """
        custom_reserved_names = ['foo', 'bar', 'eggs', 'spam']

        class CustomReservedNamesForm(forms.RegistrationForm):
            reserved_names = custom_reserved_names

        for reserved_name in custom_reserved_names:
            data = self.valid_data.copy()
            data[self.user_model.USERNAME_FIELD] = reserved_name
            form = CustomReservedNamesForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertTrue(
                form.has_error(self.user_model.USERNAME_FIELD)
            )
            self.assertTrue(
                six.text_type(validators.RESERVED_NAME) in
                form.errors[self.user_model.USERNAME_FIELD]
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

        validator_different = validators.ReservedNameValidator(
            reserved_names=[]
        )
        self.assertFalse(validator.__eq__(validator_different))

    def test_case_insensitive_validator(self):
        """
        Test the case-insensitive username validator.

        """
        validator = validators.CaseInsensitiveUnique(
            self.user_model, self.user_model.USERNAME_FIELD,
            validators.DUPLICATE_USERNAME
        )
        for value in (123456, 1.7, uuid.uuid4()):
            self.assertTrue(validator(value) is None)

        base_creation_data = self.valid_data.copy()
        base_creation_data['password'] = base_creation_data['password1']
        del base_creation_data['password1']
        del base_creation_data['password2']

        test_names = [
            (u'alice', u'ALICE'),
            (u'ALICE', u'alice'),
            (u'Alice', u'alice'),
        ]
        if six.PY3:
            test_names.extend([
                (u'STRASSBURGER', u'straßburger'),
            ])

        for name, conflict in test_names:
            creation_data = base_creation_data.copy()
            creation_data[self.user_model.USERNAME_FIELD] = name
            existing_user = self.user_model(**creation_data)
            existing_user.save()
            with self.assertRaisesMessage(
                    ValidationError,
                    six.text_type(validators.DUPLICATE_USERNAME)
            ):
                validator(conflict)
            existing_user.delete()

    def test_case_insensitive_validator_eq(self):
        """
        Test CaseInsensitiveUnique __eq__ method.
        __eq__ is necessary for serializing custom user models that use
        the validator.

        """
        validator = validators.CaseInsensitiveUnique(
            self.user_model, self.user_model.USERNAME_FIELD,
            validators.DUPLICATE_USERNAME
        )
        validator_same = validators.CaseInsensitiveUnique(
            self.user_model, self.user_model.USERNAME_FIELD,
            validators.DUPLICATE_USERNAME
        )
        self.assertTrue(validator.__eq__(validator_same))

        validator_different = validators.CaseInsensitiveUnique(
            self.user_model, 'not username field',
            validators.DUPLICATE_USERNAME
        )
        self.assertFalse(validator.__eq__(validator_different))

    def test_case_insensitive_form(self):
        """
        Test the case-insensitive registration form.

        """
        base_creation_data = self.valid_data.copy()
        base_creation_data['password'] = base_creation_data['password1']
        del base_creation_data['password1']
        del base_creation_data['password2']

        test_names = [
            (u'alice', u'ALICE'),
            (u'ALICE', u'alice'),
            (u'Alice', u'alice'),
            (u'AlIcE', u'aLiCe'),
            (u'STRASSBURGER', u'straßburger'),
        ]

        for name, conflict in test_names:
            creation_data = base_creation_data.copy()
            creation_data[self.user_model.USERNAME_FIELD] = name
            existing_user = self.user_model(**creation_data)
            existing_user.save()
            user_data = self.valid_data.copy()
            user_data[self.user_model.USERNAME_FIELD] = name
            form = forms.RegistrationFormCaseInsensitive(data=user_data)
            self.assertFalse(form.is_valid())
            self.assertTrue(
                form.has_error(self.user_model.USERNAME_FIELD)
            )
            self.assertEqual(
                [six.text_type(validators.DUPLICATE_USERNAME)],
                form.errors[self.user_model.USERNAME_FIELD]
            )
            self.assertEqual(
                1, len(form.errors[self.user_model.USERNAME_FIELD])
            )

    def test_tos_field(self):
        """
        The terms-of-service field on RegistrationFormTermsOfService
        is required.

        """
        form = forms.RegistrationFormTermsOfService(
            data=self.valid_data.copy()
        )
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('tos'))
        self.assertEqual(
            form.errors['tos'],
            [six.text_type(validators.TOS_REQUIRED)]
        )

    def test_email_uniqueness(self):
        """
        Email uniqueness is enforced by RegistrationFormUniqueEmail.

        """
        self.user_model.objects.create(
            username='bob',
            email=self.valid_data['email'],
            password=self.valid_data['password1']
        )

        form = forms.RegistrationFormUniqueEmail(
            data=self.valid_data.copy()
        )
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('email'))
        self.assertEqual(
            form.errors['email'],
            [six.text_type(validators.DUPLICATE_EMAIL)]
        )

        data = self.valid_data.copy()
        data.update(email='bob@example.com')
        form = forms.RegistrationFormUniqueEmail(
            data=data
        )
        self.assertTrue(form.is_valid())

    def test_confusables_validator(self):
        """
        Test the confusable-username validator standalone.

        """
        for dangerous_value in (
                u'p\u0430yp\u0430l',
                u'g\u043e\u043egle',
                u'\u03c1ay\u03c1al',
        ):
            with self.assertRaises(ValidationError):
                validators.validate_confusables(dangerous_value)
        for safe_value in (
                u'paypal',
                u'google',
                u'root',
                u'admin',
                u'\u041f\u0451\u0442\u0440',
                u'\u5c71\u672c',
                3,
        ):
            validators.validate_confusables(safe_value)

    def test_confusables_email_validator(self):
        """
        Test the confusable-email validator standalone.

        """
        for dangerous_value in (
                u'p\u0430yp\u0430l@example.com',
                u'g\u043e\u043egle@example.com',
                u'\u03c1ay\u03c1al@example.com',
                u'paypal@ex\u0430mple.com',
                u'google@exam\u03c1le.com'
        ):
            with self.assertRaises(ValidationError):
                validators.validate_confusables_email(dangerous_value)
        for safe_value in(
                u'paypal@example.com',
                u'google@example.com',
                u'\u041f\u0451\u0442\u0440@example.com',
                u'\u5c71\u672c@example.com',
                u'username',
        ):
            validators.validate_confusables_email(safe_value)
