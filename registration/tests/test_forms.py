"""
Exercise django-registration's built-in form classes.

"""

from django.utils.six import text_type

from .. import forms
from .base import RegistrationTestCase


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

    def test_tos_field(self):
        """
        The terms-of-service field on RegistrationFormTermsOfService
        is required.

        """
        form = forms.RegistrationFormTermsOfService(
            data=self.valid_data.copy()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['tos'],
            [text_type(forms.TOS_REQUIRED)]
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
        self.assertEqual(
            form.errors['email'],
            [text_type(forms.DUPLICATE_EMAIL)]
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
            self.assertEqual(
                form.errors['email'],
                [text_type(forms.FREE_EMAIL)]
            )

        form = forms.RegistrationFormNoFreeEmail(
            data=self.valid_data.copy()
        )
        self.assertTrue(form.is_valid())
