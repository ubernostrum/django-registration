.. _forms:
.. module:: django_registration.forms

Base form classes
=================

Several form classes are provided with django-registration,
covering common cases for gathering account information and
implementing common constraints for user registration. These forms
were designed with django-registration's built-in registration
workflows in mind, but may also be useful in other situations.


.. class:: RegistrationForm

   A form for registering an account. This is a subclass of Django's
   built-in :class:`~django.contrib.auth.forms.UserCreationForm`, and
   has the following fields, all of which are required:

   `username`
       The username to use for the new account.

   `email`
      The email address to use for the new account.

   `password1`
      The password to use for the new account.

   `password2`
      The password to use for the new account, repeated to catch
      typos.

   .. note:: **Validation of usernames**

      Django supplies a default regex-based validator for usernames in
      its base :class:`~django.contrib.auth.models.AbstractBaseUser`
      implementation, allowing any word character along with the
      following set of additional characters: `.`, `@`, `+`, and
      `-`. However, in Django 1.11 on Python 2 this regex uses the
      :data:`re.ASCII` flag, while on Python 3 it uses the
      :data:`re.UNICODE` flag. This means that if you're using Django
      1.11, the set of accepted characters will vary depending on the
      Python version you use.

      Because it's a subclass of Django's
      :class:`~django.contrib.auth.forms.UserCreationForm`,
      :class:`RegistrationForm` will inherit the base validation
      defined by Django. It also applies one custom validator:
      :class:`~django_registration.validators.ReservedNameValidator`. See
      the documentation for
      :class:`~django_registration.validators.ReservedNameValidator`
      for notes on why it exists and how to customize its behavior.


.. class:: RegistrationFormCaseInsensitive

   A subclass of :class:`RegistrationForm` which enforces
   case-insensitive uniqueness of usernames, by applying
   :class:`~django_registration.validators.CaseInsensitiveUnique`
   to the username field.

   .. note:: **Unicode case handling**

     On all versions of Python, this form will normalize the username
     value to form NFKC, matching Django's default approach to Unicode
     normalization. On Python 3, it will also case-fold the value
     (Python 3 provides a native :meth:`~str.casefold()` method on
     strings).

     The validator will then use a case-insensitive (`iexact`)
     lookup to determine if a user with the same username already
     exists; the results of this query may depend on the quality of
     your database's Unicode implementation, and on configuration
     details. The results may also be surprising to developers who are
     primarily used to English/ASCII text, as Unicode's case rules can
     be quite complex.

.. class:: RegistrationFormTermsOfService

   A subclass of :class:`RegistrationForm` which adds one additional,
   required field:

   `tos`
       A checkbox indicating agreement to the site's terms of
       service/user agreement.


.. class:: RegistrationFormUniqueEmail

   A subclass of :class:`RegistrationForm` which enforces uniqueness
   of email addresses in addition to uniqueness of usernames, by
   applying
   :class:`~django_registration.validators.CaseInsensitiveUnique` to
   the email field.
