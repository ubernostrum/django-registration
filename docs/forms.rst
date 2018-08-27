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
      The password to use for the new account. This is represented as
      a password input (``input type="password"`` in the rendered
      HTML).

   ``password2``
      The password to use for the new account. This is represented as
      a password input (``input type="password"`` in the rendered
      HTML).

   Because this is a subclass of Django's own
   :class:`~django.contrib.auth.forms.UserCreationForm`, the
   constraints on usernames and email addresses match those enforced
   by Django's default authentication backend for instances of
   :class:`~django.contrib.auth.models.User`. The repeated entry of the
   password serves to catch typos.

   .. note:: **Unicode usernames**

      There is one important difference in form behavior depending on
      the version of Python you're using. Django's username validation
      regex allows a username to contain any word character along with
      the following set of additional characters: ``.@+-``. However,
      on Python 2 this regex uses the ``ASCII`` flag (since Python 2's
      string type is ASCII by default), while on Python 3 it uses the
      ``UNICODE`` flag (since Python 3's string type is Unicode). This
      means that usernames containing non-ASCII word characters are
      only permitted when using Python 3.

   .. note:: **Validation of usernames**

      Because it's a subclass of Django's
      :class:`~django.contrib.auth.forms.UserCreationForm`,
      :class:`RegistrationForm` will inherit the base validation
      defined by Django. It also adds a custom
      :meth:`~django.forms.Form.clean()` method which applies one
      custom validator:
      :class:`~django_registration.validators.ReservedNameValidator`. See
      the documentation for
      :class:`~django_registration.validators.ReservedNameValidator`
      for notes on why it exists and how to customize its behavior.


.. class:: RegistrationFormTermsOfService

   A subclass of :class:`RegistrationForm` which adds one additional,
   required field:

   ``tos``
       A checkbox indicating agreement to the site's terms of
       service/user agreement.


.. class:: RegistrationFormUniqueEmail

   A subclass of :class:`RegistrationForm` which enforces uniqueness
   of email addresses in addition to uniqueness of usernames.
