"""
Exercise django-registration's built-in form classes.

"""

from django import get_version
from django.utils.six import text_type

from .. import forms
from .base import RegistrationTestCase
from django.utils.translation import ugettext_lazy as _


if get_version()[:3] == "1.8":  # pragma: no cover
    BAD_USERNAME = _("Enter a valid username. "
                     "This value may contain only letters, numbers "
                     "and @/./+/-/_ characters.")
else:  # pragma: no cover
    BAD_USERNAME = _("This value may contain only letters, numbers and "
                     "@/./+/-/_ characters.")

DUPLICATE_USER = _("A user with that username already exists.")
PASSWORD_MISMATCH = _("The two password fields didn't match.")


class RegistrationFormTests(RegistrationTestCase):
    """
    Test the built-in form classes.

    """
    def test_username_format(self):
        """
        Invalid usernames are rejected.

        """
        bad_usernames = [
            'user!example', 'valid?',
        ]
        for username in bad_usernames:
            data = self.valid_data.copy()
            data.update(username=username)
            form = forms.RegistrationForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertEqual(
                form.errors['username'],
                [text_type(BAD_USERNAME)]
            )

    def test_user_uniqueness(self):
        """
        Existing usernames cannot be re-used.

        """
        data = self.valid_data.copy()
        data.pop('password2')
        password = data.pop('password1')
        data['password'] = password
        self.user_model.objects.create(**data)

        form = forms.RegistrationForm(data=self.valid_data.copy())
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['username'],
            [text_type(DUPLICATE_USER)]
        )

    def test_password_match(self):
        """
        Both submitted passwords must match.

        """
        data = self.valid_data.copy()
        data.update(password2='swordfishes')
        form = forms.RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['password2'],
            [text_type(PASSWORD_MISMATCH)]
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
