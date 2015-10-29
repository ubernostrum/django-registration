.. _forms:
.. module:: registration.forms

Base form classes
=================

Several form classes are provided with ``django-registration``,
covering common cases for gathering account information and
implementing common constraints for user registration. These forms
were designed with ``django-registration``'s built-in registration
workflows in mind, but may also be useful in other situations.


.. class:: RegistrationForm

   A simple form for registering an account. It is a subclass of
   Django's `UserCreationForm <https://docs.djangoproject.com/en/1.8/topics/auth/default/#django.contrib.auth.forms.UserCreationForm>`_ and
   has the following fields, all of which are required:

   ``username``
       The username to use for the new account. This is represented as
       a text input which validates that the username is unique,
       consists entirely of alphanumeric characters and underscores
       and is at most 30 characters in length.

   ``email``
      The email address to use for the new account. This is
      represented as a text input which accepts email addresses up to
      75 characters in length.

   ``password1``
      The password to use for the new account. This represented as a
      password input (``input type="password"`` in the rendered HTML).

   ``password2``
      The password to use for the new account. This represented as a
      password input (``input type="password"`` in the rendered HTML).

   The constraints on usernames and email addresses match those
   enforced by Django's default authentication backend for instances
   of ``django.contrib.auth.models.User``. The repeated entry of the
   password serves to catch typos.


.. class:: RegistrationFormTermsOfService

   A subclass of :class:`RegistrationForm` which adds one additional,
   required field:

   ``tos``
       A checkbox indicating agreement to the site's terms of
       service/user agreement.


.. class:: RegistrationFormUniqueEmail

   A subclass of :class:`RegistrationForm` which enforces uniqueness
   of email addresses in addition to uniqueness of usernames.


.. class:: RegistrationFormNoFreeEmail

   A subclass of :class:`RegistrationForm` which disallows
   registration using addresses from some common free email
   providers. This can, in some cases, cut down on automated
   registration by spambots.

   By default, the following domains are disallowed for email
   addresses:

   * ``aim.com``

   * ``aol.com``

   * ``email.com``

   * ``gmail.com``

   * ``googlemail.com``

   * ``hotmail.com``

   * ``hushmail.com``

   * ``msn.com``

   * ``mail.ru``

   * ``mailinator.com``

   * ``live.com``

   * ``yahoo.com``

   To change this, subclass this form and set the class attribute
   ``bad_domains`` to a list of domains you wish to disallow.
