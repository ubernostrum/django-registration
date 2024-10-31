"""
Forms and validation code for user registration.

"""

# SPDX-License-Identifier: BSD-3-Clause

import warnings

from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

try:
    from django.contrib.auth.forms import SetPasswordMixin
except ImportError:
    # SetPasswordMixin was added in Django 5.1. For older Django versions, we have a
    # backported copy of it.
    from ._backports import SetPasswordMixin  # pragma: no cover

from . import validators

UserModel = get_user_model()


class BaseRegistrationForm(forms.ModelForm):
    """
    Minimal user registration form class.

    In most cases, this form should not be used directly, and :class:`RegistrationForm`
    should be used instead as the base class of user-registration forms. The primary
    difference between this class and :class:`RegistrationForm` is that
    :class:`RegistrationForm` makes some additional assumptions about which fields to
    include and includes significant custom validation logic, while this form attempts
    to be as minimal as possible with respect to included fields.

    In general, you should be using :class:`RegistrationForm` unless you are absolutely
    certain that you need to build your own custom registration form without using
    :class:`RegistrationForm`'s additional validation or fields.


    **Using a custom user model**

    Custom user models are supported, but you will need to ensure a few attributes are
    set on your custom user model to allow this form to work with it:

    * :attr:`~django.contrib.auth.models.CustomUser.EMAIL_FIELD`: a :class:`str`
      specifying the name of the field containing the user's email address.

    * :attr:`~django.contrib.auth.models.CustomUser.USERNAME_FIELD`: a :class:`str`
      specifying the name of the field containing the user's "username". If you use the
      email address as the primary "username"/identifier, set this to the same field
      name as ``EMAIL_FIELD``.

    * :attr:`~django.contrib.auth.models.CustomUser.REQUIRED_FIELDS`: a :class:`list` of
      names of fields on your user model which must be included in the form.

    Django's :class:`~django.contrib.auth.models.AbstractUser`, which is what many
    custom user models will inherit from and also what the default Django user model
    inherits from, sets all three of these, and generally for a custom model you would
    only need to override ``REQUIRED_FIELDS`` in order to specify any additional custom
    fields of your model which should be included in the form.

    However, if you have a custom user model which inherits from Django's
    :class:`~django.contrib.auth.models.AbstractBaseUser` (which is an even more minimal
    base class than ``AbstractUser``), or which does not inherit from any of Django's
    abstract base user classes, you will need to set all three of the above attributes
    on your custom user model for it to be usable with this form.

    Additionally, if you use a registration workflow which sends an email to the
    newly-registered user, your user model must implement the
    :meth:`~django.contrib.auth.models.User.email_user` method, with the same API as
    Django's implementation. If your user model inherits from ``AbstractUser``, this
    method is implemented for you automatically.


    **Fields defined on this form**

    The set of fields on this form will be all and *only* the fields listed in your user
    model's ``REQUIRED_FIELDS`` attribute. If you are using the default Django user
    model, or a subclass of :class:`~django.contrib.auth.models.AbstractUser` without
    overriding ``REQUIRED_FIELDS``, this will *not* include the username field. It also
    will *not* include any fields or logic related to setting/validating a password. It
    is assumed, if you are using this minimal base class, that you will either find this
    acceptable or be providing your own custom logic in a subclass to handle your
    particular needs.

    """

    # pylint: disable=too-few-public-methods

    class Meta:
        fields = UserModel.REQUIRED_FIELDS
        model = UserModel


class RegistrationForm(SetPasswordMixin, BaseRegistrationForm):
    """
    A form for registering a new user account.

    This is the default form class used by all included views in
    ``django-registration``, and is designed to be able to work with a wide variety of
    user models.

    If you're using Django's default :class:`~django.contrib.auth.models.User` model,
    this form will work automatically. If you're using a `custom user model
    <https://docs.djangoproject.com/en/stable/topics/auth/customizing/#substituting-a-custom-user-model>`_,
    this form can work with it so long as your user model meets certain requirements.

    This form is a :class:`~django.forms.ModelForm` which will derive fields and basic
    validation from your user model's field definitions, though it will also perform
    additional validation steps on certain fields. As a ``ModelForm``, calling
    :meth:`save` will create an instance of the user model from the validated data, save
    it to the database, and return it.

    In general you should use this form as-is, and only subclass it if you want to
    remove one or more of the additional validators applied here (if you want to supply
    *extra* validators, you can do so via subclassing, but you can also declare them on
    your user model and have them automatically picked up by this form).

    If you do find yourself needing to remove validators from this form, it may be
    better to instead write and use a subclass of :class:`BaseRegistrationForm`, which
    is a more minimal base class that does not implement any of the field or validation
    handling of this form.


    **Using a custom user model**

    Custom user models are supported, but you will need to ensure a few attributes are
    set on your custom user model to allow this form to work with it:

    * :attr:`~django.contrib.auth.models.CustomUser.EMAIL_FIELD`: a :class:`str`
      specifying the name of the field containing the user's email address.

    * :attr:`~django.contrib.auth.models.CustomUser.USERNAME_FIELD`: a :class:`str`
      specifying the name of the field containing the user's "username". If you use the
      email address as the primary "username"/identifier, set this to the same field
      name as ``EMAIL_FIELD``.

    * :attr:`~django.contrib.auth.models.CustomUser.REQUIRED_FIELDS`: a :class:`list` of
      names of fields on your user model which must be included in the form.

    Django's :class:`~django.contrib.auth.models.AbstractUser`, which is what many
    custom user models will inherit from and also what the default Django user model
    inherits from, sets all three of these, and generally for a custom model you would
    only need to override ``REQUIRED_FIELDS`` in order to specify any additional custom
    fields of your model which should be included in the form.

    However, if you have a custom user model which inherits from Django's
    :class:`~django.contrib.auth.models.AbstractBaseUser` (which is an even more minimal
    base class than ``AbstractUser``), or which does not inherit from any of Django's
    abstract base user classes, you will need to set all three of the above attributes
    on your custom user model for it to be usable with this form.

    Additionally, if you use a registration workflow which sends an email to the
    newly-registered user, your user model must implement the
    :meth:`~django.contrib.auth.models.User.email_user` method, with the same API as
    Django's implementation. If your user model inherits from ``AbstractUser``, this
    method is implemented for you automatically.


    **Fields defined on this form**

    Django's ``AbstractBaseUser`` does *not* include its username field in
    ``REQUIRED_FIELDS``. To work around that, this form will include all fields listed
    in your user model's ``REQUIRED_FIELDS`` *and* will also include the field named in
    your user model's ``USERNAME_FIELD`` if it is not included in ``REQUIRED_FIELDS``.

    If your user model's email address field is also its username field, set both
    ``EMAIL_FIELD`` and ``USERNAME_FIELD`` to that field's name, as noted above; the
    field will be included in the form only once.

    This form will also include two password fields, with field names ``password1`` and
    ``password2``, which will be used to set the user account's password. Two fields are
    used in order to implement the common UI pattern of requiring the user to enter the
    password twice and check that both entries match.


    **Validation on this form**

    In addition to any validation requirements or validators defined on your user model
    and its fields, this form will apply the following validation checks:

    * The values entered into the ``password1`` and ``password2`` fields match. If they
      do not match, the validation error will be attached to the ``password2`` field.

    * The value entered into the password fields passes `all password validators
      configured in your Django settings
      <https://docs.djangoproject.com/en/stable/topics/auth/passwords/#password-validation>`_.
      If the password fails validation, the error will be attached to the ``password2``
      field.

    * The value entered into the username field is not a case-insensitive match for any
      existing username value.

    * The value entered into the username field is not a :ref:`reserved name
      <reserved-names>`. To override the default set of reserved names, subclass this
      form and set the attribute ``reserved_names`` to the list of names you wish to
      reserve.

    * The value entered into the username field is not a "confusable" value (see the
      documentation on :ref:`preventing homograph attacks <homograph-attacks>` for an
      explanation).

    * The field named in your user model's ``EMAIL_FIELD`` attribute will have
      ``required=True`` (Django's default ``AbstractBaseUser`` sets ``blank=True`` on
      the email field, making it optional in any form which does not override this).

    * The value entered into the email address field conforms to `the HTML5 email
      validation rule
      <https://html.spec.whatwg.org/multipage/input.html#email-state-(type=email)>`_. Note
      that this validation rule is automatically enforced client-side by HTML5-compliant
      browsers as part of the implementation of ``input type="email"``, but is also
      significantly stricter than what the email RFCs allow in an address. Many unusual
      syntactic constructs which are permitted by the email RFCs are disallowed by
      HTML5's email validation and will be rejected by ``django-registration``.

    * The value entered into the email address field does not contain a "confusable"
      value in its local-part or in its domain, though the combination of the local-part
      and domain together is allowed to be "confusable".

    """

    # pylint: disable=too-few-public-methods

    error_css_class = "error"
    required_css_class = "required"

    password1, password2 = SetPasswordMixin.create_password_fields()

    class Meta(BaseRegistrationForm.Meta):
        fields = (
            UserModel.REQUIRED_FIELDS
            if UserModel.USERNAME_FIELD in UserModel.REQUIRED_FIELDS
            else [UserModel.USERNAME_FIELD] + UserModel.REQUIRED_FIELDS
        )
        field_classes = {UserModel.USERNAME_FIELD: auth_forms.UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if defined_reserved_names := getattr(self, "reserved_names", None):
            reserved_names = defined_reserved_names
        else:
            reserved_names = validators.DEFAULT_RESERVED_NAMES
        username_validators = [
            validators.ReservedNameValidator(reserved_names),
            validators.validate_confusables,
            validators.CaseInsensitiveUnique(
                UserModel, UserModel.USERNAME_FIELD, validators.DUPLICATE_USERNAME
            ),
        ]
        self.fields[UserModel.USERNAME_FIELD].validators.extend(username_validators)
        # django-registration's email validation is significantly stricter than Django's
        # default email validation, which means that leaving Django's default validation
        # on only causes confusion due to duplicate error messages (see GitHub issue
        # #238). So we apply only the django-registration validators, not the default
        # Django validator, on the email field.
        self.fields[UserModel.EMAIL_FIELD].validators = [
            validators.HTML5EmailValidator(),
            validators.validate_confusables_email,
        ]
        self.fields[UserModel.EMAIL_FIELD].required = True

    def clean(self):
        """
        Django form hook implementing form-wide validation logic, including logic
        that must check multiple fields simultaneously. Here, this hook is used to check
        the two password fields to ensure they match.

        """
        self.validate_passwords()
        return super().clean()

    def _post_clean(self):
        """
        ModelForm-specific validation hook which runs during validation but after
        the model instance has been created.

        This is not part of the public API of ModelForm, but is used because it is the
        only place in the validation process where it's possible to run the password
        validators, since some password validators need to check the full user-model
        instance. Django's ``UserCreationForm`` uses the same hook in the same way.

        """
        super()._post_clean()
        self.validate_password_for_user(self.instance)

    def save(self, commit=True):
        """
        Django ModelForm hook for creating and returning the new user model
        instance. If ``commit=True``, the instance will be saved to the database; if
        ``commit=False``, the instance will *not* be saved before being returned.

        """
        user = super().save(commit=False)
        user = self.set_password_and_save(user, commit=commit)
        if commit and hasattr(self, "save_m2m"):
            self.save_m2m()
        return user


class RegistrationFormCaseInsensitive(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` enforcing case-insensitive uniqueness of
    usernames.

    This form class is no longer needed, as the default :class:`RegistrationForm` now
    enforces the same uniqueness requirement by default; use of this form class is
    deprecated, and it will be removed in django-registration 6.0.

    """

    def __init__(self, *args, **kwargs):
        warnings.warn(  # pragma: no cover
            "RegistrationFormCaseInsensitive is deprecated and will be removed "
            "in django-registration 6.0. Use the base RegistrationForm instead; as "
            "of django-registration 5.1, it enforces case-insensitive uniqueness of "
            "usernames (and Django's own UserCreationForm does so as of Django 4.2).",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)  # pragma: no cover


class RegistrationFormTermsOfService(RegistrationForm):
    """
    A subclass of :class:`RegistrationForm` which adds one extra required field: a
    checkbox named ``tos`` indicating agreement to a site's terms of service.

    """

    tos = forms.BooleanField(
        widget=forms.CheckboxInput,
        label=_("I have read and agree to the Terms of Service"),
        error_messages={"required": validators.TOS_REQUIRED},
    )


class RegistrationFormUniqueEmail(RegistrationForm):
    """
    A subclass of ``RegistrationForm`` which enforces uniqueness of email addresses.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        email_field = UserModel.get_email_field_name()
        self.fields[email_field].validators.append(
            validators.CaseInsensitiveUnique(
                UserModel, email_field, validators.DUPLICATE_EMAIL
            )
        )
