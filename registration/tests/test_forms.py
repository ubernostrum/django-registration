"""
Exercise django-registration's built-in form classes.

"""
import uuid

from django.core.exceptions import ValidationError
from django.test import modify_settings
from django.utils.six import text_type

from .. import forms
from .. import validators
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
        self.assertTrue(form.has_error(self.user_model.USERNAME_FIELD))

    def test_reserved_names(self):
        """
        Reserved names are disallowed.

        """
        for reserved_name in validators.DEFAULT_RESERVED_NAMES:
            data = self.valid_data.copy()
            data[self.user_model.USERNAME_FIELD] = reserved_name
            form = forms.RegistrationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error(self.user_model.USERNAME_FIELD))
            self.assertTrue(
                text_type(validators.RESERVED_NAME) in
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
            self.assertTrue(form.has_error(self.user_model.USERNAME_FIELD))
            self.assertTrue(
                text_type(validators.CONFUSABLE) in
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
                text_type(validators.CONFUSABLE_EMAIL) in
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
            self.assertTrue(form.has_error(self.user_model.USERNAME_FIELD))
            self.assertTrue(
                text_type(validators.RESERVED_NAME) in
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
            [text_type(validators.TOS_REQUIRED)]
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
            [text_type(validators.DUPLICATE_EMAIL)]
        )

        data = self.valid_data.copy()
        data.update(email='bob@example.com')
        form = forms.RegistrationFormUniqueEmail(
            data=data
        )
        self.assertTrue(form.is_valid())

    def test_no_free_email(self):
        """
        Free email domains are disallowed by
        RegistrationFormNoFreeEmail.

        """
        for domain in forms.RegistrationFormNoFreeEmail.bad_domains:
            data = self.valid_data.copy()
            data.update(
                email='testuser@%s' % domain
            )
            form = forms.RegistrationFormNoFreeEmail(
                data=data
            )
            self.assertFalse(form.is_valid())
            self.assertTrue(form.has_error('email'))
            self.assertEqual(
                form.errors['email'],
                [text_type(validators.FREE_EMAIL)]
            )

        form = forms.RegistrationFormNoFreeEmail(
            data=self.valid_data.copy()
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
