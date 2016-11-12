"""
Exercise django-registration's built-in form classes.

"""

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
