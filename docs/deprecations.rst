.. _deprecations:


Feature and API deprecation cycle
=================================

This document will list any features or APIs of ``django-registration`` which
are deprecated and scheduled to be removed in future releases.

As of |release|, the following features or APIs are deprecated:

* The form class
  ``django_registration.forms.RegistrationFormCaseInsensitive``. This was
  previously provided because the default
  :class:`~django_registration.forms.RegistrationForm` did *not* enforce
  case-insensitive uniqueness of the username value. Now that
  ``RegistrationForm`` does enforce that, this class serves no purpose and is
  deprecated. It will be removed in ``django-registration`` 6.0.
