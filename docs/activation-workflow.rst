.. _activation-workflow:
.. module:: django_registration.backends.activation

The two-step activation workflow
================================

The two-step activation workflow, found in
``django_registration.backends.activation``, implements a two-step registration
process: a user signs up, an inactive account is created, and an email is sent
containing an activation link which must be clicked to make the account active.


Behavior and configuration
--------------------------

A default URLconf is provided, which you can :func:`~django.urls.include` in
your URL configuration; that URLconf is
``django_registration.backends.activation.urls``. For example, to place user
registration under the URL prefix ``/accounts/``, you could place the following
in your root URLconf:

.. code-block:: python

   from django.urls import include, path

   urlpatterns = [
       # Other URL patterns ...
       path('accounts/', include('django_registration.backends.activation.urls')),
       path('accounts/', include('django.contrib.auth.urls')),
       # More URL patterns ...
   ]

That also sets up the views from ``django.contrib.auth`` (login, logout, password
reset, etc.).

This workflow makes use of up to three settings (click for details on each):

* :data:`~django.conf.settings.ACCOUNT_ACTIVATION_DAYS`

* :data:`~django.conf.settings.REGISTRATION_OPEN`

* :data:`~django.conf.settings.REGISTRATION_SALT` (see also :ref:`note below
  <salt-security>`)

By default, this workflow uses
:class:`~django_registration.forms.RegistrationForm` as its form class for user
registration; this can be overridden by passing the keyword argument
``form_class`` to the registration view.


Views
-----

.. currentmodule:: django_registration.backends.activation.views

Two views are provided to implement the signup/activation process. These
subclass :ref:`the base views of django-registration <views>`, so anything that
can be overridden/customized there can equally be overridden/customized
here. There are some additional customization points specific to this
implementation, which are listed below.

For an overview of the templates used by these views (other than those
specified below), and their context variables, see :ref:`the quick start guide
<default-templates>`.


.. class:: RegistrationView

   A subclass of :class:`django_registration.views.RegistrationView`
   implementing the signup portion of this workflow.

   Important customization points unique to this class are:

   .. method:: create_inactive_user(form)

      Creates and returns an inactive user account, and calls
      :meth:`send_activation_email()` to send the email with the activation
      key. The argument ``form`` is a valid registration form instance passed
      from :meth:`~django_registration.views.RegistrationView.register()`.

      :param django_registration.forms.RegistrationForm form: The registration form.
      :rtype: django.contrib.auth.models.AbstractUser

   .. method:: get_activation_key(user)

      Given an instance of the user model, generates and returns an activation
      key (a string) for that user account.

      :param django.contrib.auth.models.AbstractUser user: The new user account.
      :rtype: str

   .. method:: get_email_context(activation_key)

      Returns a dictionary of values to be used as template context when
      generating the activation email.

      :param str activation_key: The activation key for the new user account.
      :rtype: dict

   .. method:: send_activation_email(user)

      Given an inactive user account, generates and sends the activation email
      for that account.

      :param django.contrib.auth.models.AbstractUser user: The new user account.
      :rtype: None

   .. attribute:: email_body_template

      A string specifying the template to use for the body of the activation
      email. Default is ``"django_registration/activation_email_body.txt"``.

   .. attribute:: email_subject_template

      A string specifying the template to use for the subject of the activation
      email. Default is
      ``"django_registration/activation_email_subject.txt"``. Note that, to avoid
      `header-injection vulnerabilities
      <https://en.wikipedia.org/wiki/Email_injection>`_, the result of
      rendering this template will be forced into a single line of text,
      stripping newline characters.

.. class:: ActivationView

   A subclass of :class:`django_registration.views.ActivationView` implementing
   the activation portion of this workflow.

   Errors in activating the user account will raise
   :exc:`~django_registration.exceptions.ActivationError`, with one of the
   following values for the exception's ``code``:

   ``"already_activated"``
       Indicates the account has already been activated.

   ``"bad_username"``
       Indicates the username decoded from the activation key is invalid (does
       not correspond to any user account).

   ``"expired"``
       Indicates the account/activation key has expired.

   ``"invalid_key"``
      Generic indicator that the activation key was invalid.

   Important customization points unique to this class are:

   .. method:: get_user(username)

      Given a username (determined by the activation key), looks up and returns
      the corresponding instance of the user model. If no such account exists,
      raises :exc:`~django_registration.exceptions.ActivationError` as
      described above. In the base implementation, checks the
      :attr:`~django.contrib.auth.models.User.is_active` field to avoid
      re-activating already-active accounts, and raises
      :exc:`~django_registration.exceptions.ActivationError` with code
      ``already_activated`` to indicate this case.

      :param str username: The username of the new user account.
      :rtype: django.contrib.auth.models.AbstractUser
      :raises django_registration.exceptions.ActivationError: if no
         matching inactive user account exists.

   .. method:: validate_key(activation_key)

      Given the activation key, verifies that it carries a valid signature and
      a timestamp no older than the number of days specified in the setting
      ``ACCOUNT_ACTIVATION_DAYS``, and returns the username from the activation
      key. Raises :exc:`~django_registration.exceptions.ActivationError`, as
      described above, if the activation key has an invalid signature or if the
      timestamp is too old.

      :param str activation_key: The activation key for the new user account.
      :rtype: str
      :raises django_registration.exceptions.ActivationError: if the
         activation key has an invalid signature or is expired.

   .. note:: **URL patterns for activation**

      Although the actual value used in the activation key is the new user
      account's username, the URL pattern for :class:`~views.ActivationView`
      does not need to match all possible legal characters in a username. The
      activation key that will be sent to the user (and thus matched in the
      URL) is produced by :func:`django.core.signing.dumps()`, which
      base64-encodes its output. Thus, the only characters this pattern needs
      to match are those from `the URL-safe base64 alphabet
      <http://tools.ietf.org/html/rfc4648#section-5>`_, plus the colon ("``:``")
      which is used as a separator.

      The default URL pattern for the activation view in
      ``django_registration.backends.activation.urls`` handles this for you.


How it works
------------

When a user signs up, the activation workflow creates a new user instance to
represent the account, and sets the ``is_active`` field to :data:`False`. It then
sends an email to the address provided during signup, containing a link to
activate the account. When the user clicks the link, the activation view sets
``is_active`` to :data:`True`, after which the user can log in.

The activation key is the username of the new account, signed using `Django's
cryptographic signing tools
<https://docs.djangoproject.com/en/stable/topics/signing/>`_ (specifically,
:func:`~django.core.signing.dumps()` is used, to produce a guaranteed-URL-safe
value). The activation process includes verification of the signature prior to
activation, as well as verifying that the user is activating within the
permitted window (as specified in the setting
:data:`~django.conf.settings.ACCOUNT_ACTIVATION_DAYS`, mentioned above),
through use of Django's :class:`~django.core.signing.TimestampSigner`.


Security considerations
-----------------------

The activation key emailed to the user in the activation workflow is a value
obtained by using Django's cryptographic signing tools. The activation key is
of the form::

    encoded_username:timestamp:signature

where ``encoded_username`` is the username of the new account, ``timestamp`` is the
timestamp of the time the user registered, and ``signature`` is an HMAC of the
username and timestamp. The username and HMAC will be URL-safe base64 encoded;
the timestamp will be base62 encoded.

Django's implementation uses the value of the
:data:`~django.conf.settings.SECRET_KEY` setting as the key for HMAC;
additionally, it permits the specification of a salt value which can be used to
"namespace" different uses of HMAC across a Django-powered site.

.. _salt-security:

The activation workflow will use the value (a string) of the setting
:data:`~django.conf.settings.REGISTRATION_SALT` as the salt, defaulting to the
string ``"registration"`` if that setting is not specified. This value does *not*
need to be kept secret (only :data:`~django.conf.settings.SECRET_KEY` does); it
serves only to ensure that other parts of a site which also produce signed
values from user input could not be used as a way to generate activation keys
for arbitrary usernames (and vice-versa).
