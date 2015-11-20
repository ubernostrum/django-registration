"""
Forms and validation code for user registration.

Note that all of these forms assume your user model is similar in
structure to Django's default User class. If your user model is
significantly different, you may need to write your own form class;
see the documentation for notes on custom user models with
django-registration.

"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _


DUPLICATE_EMAIL = _("This email address is already in use. "
                    "Please supply a different email address.")
FREE_EMAIL = _("Registration using free email addresses is prohibited. "
               "Please supply a different email address.")
TOS_REQUIRED = _("You must agree to the terms to register")

User = get_user_model()


class RegistrationForm(UserCreationForm):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should take care when overriding ``save()`` to respect
    the ``commit=False`` argument, as several registration workflows
    will make use of it to create inactive user accounts.

    """
    class Meta(UserCreationForm.Meta):
        fields = [
            User.USERNAME_FIELD,
            'email',
            'password1',
            'password2'
        ]
        required_css_class = 'required'


class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.

    """
    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=_('I have read and agree to the Terms of Service'),
        error_messages={
            'required': TOS_REQUIRED,
        }
    )


class RegistrationFormUniqueEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which enforces uniqueness of
    email addresses.

    """
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(DUPLICATE_EMAIL)
        return self.cleaned_data['email']


class RegistrationFormNoFreeEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which disallows registration with
    email addresses from popular free webmail services; moderately
    useful for preventing automated spam registrations.

    To change the list of banned domains, subclass this form and
    override the attribute ``bad_domains``.

    """
    bad_domains = ['aim.com', 'aol.com', 'email.com', 'gmail.com',
                   'googlemail.com', 'hotmail.com', 'hushmail.com',
                   'msn.com', 'mail.ru', 'mailinator.com', 'live.com',
                   'yahoo.com']

    def clean_email(self):
        """
        Check the supplied email address against a list of known free
        webmail domains.

        """
        email_domain = self.cleaned_data['email'].split('@')[1]
        if email_domain in self.bad_domains:
            raise forms.ValidationError(FREE_EMAIL)
        return self.cleaned_data['email']
