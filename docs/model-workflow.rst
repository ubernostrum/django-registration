.. _model-workflow:
.. module:: registration.backends.model_activation

The model-based activation workflow
===================================

This workflow implements a two-step -- registration, followed by
activation -- process for user signup. 

.. note:: **Use of the model-based workflow is discouraged**

   The model-based activation workflow was originally the *only*
   workflow built in to ``django-registration``, and later was the
   default one. However, it no longer represents the best practice for
   registration with modern versions of Django, and so it continues to
   be included only for backwards compatibility with existing
   installations of ``django-registration``.

   If you're setting up a new installation and want a two-step process
   with activation, it's recommended you use :ref:`the HMAC activation
   workflow <hmac-workflow>` instead.

   Also, note that this workflow was previously found in
   ``registration.backends.default``, and imports from that location
   still function in ``django-registration`` |version| but now raise
   deprecation warnings. The correct location going forward is
   ``registration.backends.model_activation``.


Default behavior and configuration
----------------------------------

To make use of this workflow, simply add ``registration`` to your
``INSTALLED_APPS``, run ``manage.py migrate`` to install its model,
and include the URLconf
``registration.backends.model_activation.urls`` at whatever location
you choose in your URL hierarchy. For example:

.. code-block:: python

   from django.conf.urls import include, url

   urlpatterns = [
       # Other URL patterns ...
       url(r'^accounts/', include('registration.backends.model_activation.urls')),
       # More URL patterns ...
   ]

This workflow makes use of the following settings:

* :data:`~django.conf.settings.ACCOUNT_ACTIVATION_DAYS`

* :data:`~django.conf.settings.REGISTRATION_OPEN`

By default, this workflow uses
:class:`registration.forms.RegistrationForm` as its form class for
user registration; this can be overridden by passing the keyword
argument ``form_class`` to the registration view.

Two views are provided:
``registration.backends.model_activation.views.RegistrationView`` and
``registration.backends.model_activation.views.ActivationView``. These
views subclass ``django-registration``'s base
:class:`~registration.views.RegistrationView` and
:class:`~registration.views.ActivationView`, respectively, and
implement the two-step registration/activation process.

Upon successful registration -- not activation -- the user will be
redirected to the URL pattern named ``registration_complete``.

Upon successful activation, the user will be redirected to the URL
pattern named ``registration_activation_complete``.

This workflow uses the same templates and contexts as :ref:`the HMAC
activation workflow <hmac-workflow>`, which is covered in :ref:`the
quick-start guide <default-templates>`. Refer to the quick-start guide
for documentation on those templates and their contexts.


How account data is stored for activation
-----------------------------------------

During registration, a new instance of the user model (by default,
Django's ``django.contrib.auth.models.User`` -- see :ref:`the custom
user documentation <custom-user>` for notes on using a different
model) is created to represent the new account, with the ``is_active``
field set to ``False``. An email is then sent to the email address of
the account, containing a link the user must click to activate the
account; at that point the ``is_active`` field is set to ``True``, and
the user may log in normally.

Activation is handled by generating and storing an activation key in
the database, using the following model:


.. currentmodule:: registration.models

.. class:: RegistrationProfile

   A simple representation of the information needed to activate a new
   user account. This is **not** a user profile; it simply provides a
   place to temporarily store the activation key and determine whether
   a given account has been activated.

   Has the following fields:

   .. attribute:: user

      A ``OneToOneField`` to the user model, representing the user
      account for which activation information is being stored.

   .. attribute:: activation_key

      A 40-character ``CharField``, storing the activation key for the
      account. Initially, the activation key is the hex digest of a
      SHA1 hash; after activation, this is reset to :attr:`ACTIVATED`.

   Additionally, one class attribute exists:

   .. attribute:: ACTIVATED

      A constant string used as the value of :attr:`activation_key`
      for accounts which have been activated.

   And the following methods:

   .. method:: activation_key_expired()

      Determines whether this account's activation key has expired,
      and returns a boolean (``True`` if expired, ``False``
      otherwise). Uses the following algorithm:

      1. If :attr:`activation_key` is :attr:`ACTIVATED`, the account
         has already been activated and so the key is considered to
         have expired.

      2. Otherwise, the date of registration (obtained from the
         ``date_joined`` field of :attr:`user`) is compared to the
         current date; if the span between them is greater than the
         value of the setting ``ACCOUNT_ACTIVATION_DAYS``, the key is
         considered to have expired.

      :rtype: bool

   .. method:: send_activation_email(site)

      Sends an activation email to the address of the account.

      The activation email will make use of two templates:
      ``registration/activation_email_subject.txt`` and
      ``registration/activation_email.txt``, which are used for the
      subject of the email and the body of the email,
      respectively. Each will receive the following context:

      ``activation_key``
          The value of :attr:`activation_key`.

      ``expiration_days``
          The number of days the user has to activate, taken from the
          setting ``ACCOUNT_ACTIVATION_DAYS``.

      ``site``
          An object representing the site on which the account was
          registered; depending on whether ``django.contrib.sites`` is
          installed, this may be an instance of either
          ``django.contrib.sites.models.Site`` (if the sites
          application is installed) or
          ``django.contrib.sites.models.RequestSite`` (if
          not). Consult `the documentation for the Django sites
          framework
          <http://docs.djangoproject.com/en/dev/ref/contrib/sites/>`_
          for details regarding these objects' interfaces.

      Note that, to avoid header-injection vulnerabilities, the
      rendered output of ``registration/activation_email_subject.txt``
      will be forcibly condensed to a single line.

      :param site: An object representing the site on which account
         was registered.
      :type site: ``django.contrib.sites.models.Site`` or
        ``django.contrib.sites.models.RequestSite``
      :rtype: ``None``


Additionally, :class:`RegistrationProfile` has a custom manager
(accessed as ``RegistrationProfile.objects``):


.. class:: RegistrationManager

   This manager provides several convenience methods for creating and
   working with instances of :class:`RegistrationProfile`:

   .. method:: activate_user(activation_key)

      Validates ``activation_key`` and, if valid, activates the
      associated account by setting its ``is_active`` field to
      ``True``. To prevent re-activation of accounts, the
      :attr:`~RegistrationProfile.activation_key` of the
      :class:`RegistrationProfile` for the account will be set to
      :attr:`RegistrationProfile.ACTIVATED` after successful
      activation.

      Returns the user instance representing the account if
      activation is successful, ``False`` otherwise.

      :param activation_key: The activation key to use for the
         activation.
      :type activation_key: string, a 40-character SHA1 hexdigest
      :rtype: user or bool

   .. method:: delete_expired_users

      Removes expired instances of :class:`RegistrationProfile`, and
      their associated user accounts, from the database. This is
      useful as a periodic maintenance task to clean out accounts
      which registered but never activated.

      Accounts to be deleted are identified by searching for instances
      of :class:`RegistrationProfile` with expired activation keys and
      with associated user accounts which are inactive (have their
      ``is_active`` field set to ``False``). To disable a user account
      without having it deleted, simply delete its associated
      :class:`RegistrationProfile`; any ``User`` which does not have
      an associated :class:`RegistrationProfile` will not be deleted.

      A custom management command is provided which will execute this
      method, suitable for use in cron jobs or other scheduled
      maintenance tasks: ``manage.py cleanupregistration``.

      :rtype: ``None``

   .. method:: create_inactive_user(username, email, password, site[, send_email])

      Creates a new, inactive user account and an associated instance
      of :class:`RegistrationProfile`, sends the activation email and
      returns the new ``User`` object representing the account.

      :param username: The username to use for the new account.
      :type username: string
      :param email: The email address to use for the new account.
      :type email: string
      :param password: The password to use for the new account.
      :type password: string
      :param site: An object representing the site on which the
         account is being registered.
      :type site: ``django.contrib.sites.models.Site`` or
         ``django.contrib.sites.models.RequestSite``
      :param send_email: If ``True``, the activation email will be
         sent to the account (by calling
         :meth:`RegistrationProfile.send_activation_email`). If
         ``False``, no email will be sent (but the account will still
         be inactive).
      :type send_email: bool
      :rtype: user

   .. method:: create_profile(user)

      Creates and returns a :class:`RegistrationProfile` instance for
      the account represented by ``user``.

      The ``RegistrationProfile`` created by this method will have its
      :attr:`~RegistrationProfile.activation_key` set to a SHA1 hash
      generated from a combination of the account's username and a
      random salt.

      :param user: The user account; an instance of
         ``django.contrib.auth.models.User``.
      :type user: ``User``
      :rtype: ``RegistrationProfile``
