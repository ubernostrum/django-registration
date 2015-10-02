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
from django.utils.translation import ugettext_lazy as _


BAD_USERNAME = _("This value may contain only letters, "
                 "numbers and @/./+/-/_ characters.")
DUPLICATE_EMAIL = _("This email address is already in use. "
                    "Please supply a different email address.")
FREE_EMAIL = _("Registration using free email addresses is prohibited. "
               "Please supply a different email address.")
DUPLICATE_USER = _("A user with that username already exists.")
PASSWORD_MISMATCH = _("The two password fields didn't match.")
TOS_REQUIRED = _("You must agree to the terms to register")

User = get_user_model()


class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.

    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.

    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the registration
    view..

    """
    required_css_class = 'required'

    username = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=30,
        label=_("Username"),
        error_messages={
            'invalid': BAD_USERNAME,
        })
    email = forms.EmailField(label=_("E-mail"))
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label=_("Password (again)"))

    def clean_username(self):
        """
        Validate that the username is not already in use.

        """
        existing = User.objects.filter(
            username__iexact=self.cleaned_data['username']
        )
        if existing.exists():
            raise forms.ValidationError(DUPLICATE_USER)
        else:
            return self.cleaned_data['username']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and \
           'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != \
               self.cleaned_data['password2']:
                raise forms.ValidationError(
                    PASSWORD_MISMATCH
                )
        return self.cleaned_data


class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.

    """
    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=_(u'I have read and agree to the Terms of Service'),
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
