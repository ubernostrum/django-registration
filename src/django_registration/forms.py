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

from . import validators


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
            User.get_email_field_name(),
            'password1',
            'password2'
        ]

    error_css_class = 'error'
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        email_field = User.get_email_field_name()
        if hasattr(self, 'reserved_names'):
            reserved_names = self.reserved_names
        else:
            reserved_names = validators.DEFAULT_RESERVED_NAMES
        username_validators = [
            validators.ReservedNameValidator(reserved_names),
            validators.validate_confusables
        ]
        self.fields[User.USERNAME_FIELD].validators.extend(username_validators)
        self.fields[email_field].validators.append(
            validators.validate_confusables_email
        )
        self.fields[email_field].required = True


class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.

    """
    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=_(u'I have read and agree to the Terms of Service'),
        error_messages={
            'required': validators.TOS_REQUIRED,
        }
    )


class RegistrationFormUniqueEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which enforces uniqueness of
    email addresses.

    """
    def clean(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        email_field = User.get_email_field_name()
        email_value = self.cleaned_data.get(email_field)
        if email_value is not None:
            if User.objects.filter(**{
                    '{}__iexact'.format(email_field): email_value
            }).exists():
                self.add_error(
                    email_field,
                    forms.ValidationError(validators.DUPLICATE_EMAIL)
                )
        super(RegistrationForm, self).clean()
