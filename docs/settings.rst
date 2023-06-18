.. _settings:
.. module:: django.conf.settings


Custom settings
===============

Although the choice of registration workflow does not necessarily require
changes to your Django settings (as registration workflows are selected by
including the appropriate URL patterns in your root URLconf), the built-in
workflows of django-registration make use of several custom settings.


.. data:: ACCOUNT_ACTIVATION_DAYS

   An :class:`int` indicating how long (in days) after signup an account has in
   which to activate.

   Used by:

   * :ref:`The two-step activation workflow <activation-workflow>`


.. data:: REGISTRATION_OPEN

   A :class:`bool` indicating whether registration of new accounts is currently
   permitted.

   A default of :data:`True` is assumed when this setting is not supplied, so
   specifying it is optional unless you want to temporarily close registration
   (in which case, set it to :data:`False`).

   Used by:

   * :ref:`The two-step activation workflow <activation-workflow>`

   * :ref:`The one-step workflow <one-step-workflow>`

   Third-party workflows wishing to use an alternate method of determining
   whether registration is allowed should subclass
   :class:`django_registration.views.RegistrationView` (or a subclass of it
   from an existing workflow) and override
   :meth:`~django_registration.views.RegistrationView.registration_allowed`.


.. data:: REGISTRATION_SALT

   A :class:`str` used as an additional "salt" in the process of generating
   signed activation keys.

   This setting is optional, and a default of ``"registration"`` will be used if
   not specified. The value of this setting does not need to be kept secret;
   see :ref:`the note about this salt value and security <salt-security>` for
   details.

   Used by:

   * :ref:`The two-step activation workflow <activation-workflow>`
