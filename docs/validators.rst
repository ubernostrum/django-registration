.. _validators:
.. module:: django_registration.validators

Validation utilities
====================

To ease the process of validating user registration data,
django-registration includes some validation-related data and
utilities in ``django_registration.validators``.

The available error messages are:

.. data:: DUPLICATE_EMAIL

   Error message raised by
   :class:`~django_registration.forms.RegistrationFormUniqueEmail` when the
   supplied email address is not unique.

.. data:: DUPLICATE_USERNAME

   Error message raised by
   :class:`~django_registration.validators.CaseInsensitiveValidator`
   when the supplied username is not unique. This is the same string
   raised by Django's default
   :class:`~django.contrib.auth.models.User` model for a non-unique
   username.

.. data:: FREE_EMAIL

   Error message raised by
   :class:`~django_registration.forms.RegistrationFormNoFreeEmail` when the
   supplied email address is rejected by its list of free-email
   domains.

.. data:: RESERVED_NAME

   Error message raised by
   :class:`~django_registration.validators.ReservedNameValidator` when it is
   given a value that is a reserved name.

.. data:: TOS_REQUIRED

   Error message raised by
   :class:`~django_registration.forms.RegistrationFormTermsOfService` when
   the terms-of-service field is not checked.


All of these error messages are marked for translation; most have
translations into multiple languages already in
django-registration.

Additionally, several custom validators are provided:

.. class:: ReservedNameValidator

   A custom validator (see `Django's validators documentation
   <https://docs.djangoproject.com/en/stable/ref/forms/validation/#using-validators>`_)
   which prohibits the use of a reserved name as the value.

   By default, this validator is applied to the username field of
   :class:`django_registration.forms.RegistrationForm` and all of its
   subclasses. The validator is applied in a form-level
   :meth:`~django.forms.Form.clean` method on
   :class:`~django_registration.forms.RegistrationForm`, so to remove
   it (not recommended), subclass
   :class:`~django_registration.forms.RegistrationForm` and override
   :meth:`~django.forms.Form.clean`. For no custom form-level
   validation, you could implement it as:

   .. code-block:: python

      def clean(self):
          pass

   If you want to supply your own custom list of reserved names, you
   can subclass :class:`~django_registration.forms.RegistrationForm`
   and set the attribute ``reserved_names`` to the list of values you
   want to disallow.

   .. note:: **Why reserved names are reserved**

      Many Web applications enable per-user URLs (to display account
      information), and some may also create email addresses or even
      subdomains, based on a user's username. While this is often
      useful, it also represents a risk: a user might register a name
      which conflicts with an important URL, email address or
      subdomain, and this might give that user control over it.

      django-registration includes a list of reserved names, and
      rejects them as usernames by default, in order to avoid this
      issue.

   The default list of reserved names, if you don't specify one, is
   :data:`~django_registration.validators.DEFAULT_RESERVED_NAMES`. The
   validator will also reject any value beginning with the string
   ``".well-known"`` (see `RFC 5785
   <https://www.ietf.org/rfc/rfc5785.txt>`_).

Several constants are provided which are used by this validator:

.. data:: SPECIAL_HOSTNAMES

   A list of hostnames with reserved or special meaning (such as
   "autoconfig", used by some email clients to automatically discover
   configuration data for a domain).

.. data:: PROTOCOL_HOSTNAMES

   A list of protocol-specific hostnames sites commonly want to
   reserve, such as "www" and "mail".

.. data:: CA_ADDRESSES

   A list of email usernames commonly used by certificate authorities
   when verifying identity.

.. data:: RFC_2142

   A list of common email usernames specified by `RFC 2142
   <https://www.ietf.org/rfc/rfc2142.txt>`_.

.. data:: NOREPLY_ADDRESSES

   A list of common email usernames used for automated messages from a
   Web site (such as "noreply" and "mailer-daemon").

.. data:: SENSITIVE_FILENAMES

   A list of common filenames with important meanings, such that
   usernames should not be allowed to conflict with them (such as
   "favicon.ico" and "robots.txt").

.. data:: OTHER_SENSITIVE_NAMES

   Other names, not covered by the above lists, which have the
   potential to conflict with common URLs or subdomains, such as
   "blog" and "docs".

.. data:: DEFAULT_RESERVED_NAMES

   A list made of the concatenation of all of the above lists, used as
   the default set of reserved names for
   :class:`~django_registration.validators.ReservedNameValidator`.


.. class:: CaseInsensitiveValidator(model, field_name)

   A validator which enforces case-insensitive uniqueness on a
   particular field. Used by
   :class:`~django_registration.forms.RegistrationFormCaseInsensitive`
   for case-insensitive username uniqueness.

   :param django.db.models.Model model: The model class to query
      against for uniqueness checks.
   :param str field_name: The field name to perform the uniqueness
      check against.


.. function:: validate_confusables(value)

   A custom validator which prohibits the use of
   dangerously-confusable usernames.

   Django permits broad swaths of Unicode to be used in usernames;
   while this is useful for serving a worldwide audience, it also
   creates the possibility of `homograph attacks
   <https://en.wikipedia.org/wiki/IDN_homograph_attack>`_ through the
   use of characters which are easily visually confused for each other
   (for example, "pаypаl" contains a Cyrillic "а", visually
   indistinguishable in many fonts from a Latin "а").

   This validator will reject any mixed-script value (as defined by
   Unicode 'Script' property) which also contains one or more
   characters that appear in the Unicode Visually Confusable
   Characters file.

   This validator is enabled by default on the username field of
   registration forms.

   :param str value: The username value to validate (non-string
      usernames will not be checked)
   :raises django.core.exceptions.ValidationError: if the value is mixed-script confusable

.. function:: validate_confusables_email(value)

   A custom validator which prohibits the use of
   dangerously-confusable email address.

   Django permits broad swaths of Unicode to be used in email
   addresses; while this is useful for serving a worldwide audience,
   it also creates the possibility of `homograph attacks
   <https://en.wikipedia.org/wiki/IDN_homograph_attack>`_ through the
   use of characters which are easily visually confused for each other
   (for example, "pаypаl" contains a Cyrillic "а", visually
   indistinguishable in many fonts from a Latin "а").

   This validator will reject any email address where either the
   local-part of the domain is -- when considered in isolation --
   dangerously confusable. A string is dangerously confusable if it is
   a mixed-script value (as defined by Unicode 'Script' property)
   which also contains one or more characters that appear in the
   Unicode Visually Confusable Characters file.

   This validator is enabled by default on the email field of
   registration forms.

   :param str value: The email address to validate
   :raises django.core.exceptions.ValidationError: if the value is mixed-script confusable
