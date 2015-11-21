.. _settings:
.. module:: django.conf.settings


Custom settings
===============

Although the choice of registration workflow does not necessarily
require changes to your Django settings (as registration workflows are
selected by including the appropriate URL patterns in your root
URLconf), the built-in workflows of ``django-registration`` make use
of several custom settings.


.. data:: ACCOUNT_ACTIVATION_DAYS

   An ``int`` indicating how long (in days) after signup an account
   has in which to activate.

   This setting is required if using one of the built-in two-step
   workflows:

   * :ref:`The two-step HMAC activation workflow <hmac-workflow>`

   * :ref:`The model-based activation workflow <model-workflow>`


.. data:: REGISTRATION_OPEN

   A ``bool`` indicating whether registration of new accounts is
   currently permitted.

   A default of ``True`` is assumed when this setting is not supplied,
   so specifying it is optional unless you want to temporarily close
   registration (in which case, set it to ``False``).

   Used by: 

   * :ref:`The two-step HMAC activation workflow <hmac-workflow>`

   * :ref:`The simple one-step workflow <simple-workflow>`

   * :ref:`The model-based activation workflow <model-workflow>`

   Third-party workflows wishing to use an alternate method of
   determining whether registration is allowed should subclass
   :class:`registration.views.RegistrationView` (or a subclass of it
   from an existing workflow) and override
   :meth:`~registration.views.RegistrationView.registration_allowed`.


.. data:: REGISTRATION_SALT

   A ``str`` used as an additional "salt" in the process of generating
   HMAC-signed activation keys.

   This setting is optional, and a default of ``"registration"`` will
   be used if not specified. The value of this setting does not need
   to be kept secret; it is used solely as a way of namespacing HMAC
   usage.

   Used by:

   * :ref:`The two-step HMAC activation workflow <hmac-workflow>`
