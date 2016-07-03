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


.. data:: ACCOUNT_ACTIVATION_EMAIL_SUBJECT_TEMPLATE

   A ``path`` to a plain-text template used to render activation email subject.

   This setting is optional, and a default of
   ``registration/activation_email_subject.html`` will be used if not specified.

   A ``TemplateSyntaxError`` will be raised if the specified template could not
   be found.

   Used by:

   * :ref:`The two-step HMAC activation workflow <hmac-workflow>`

   * :ref:`The model-based activation workflow <model-workflow>`


.. data:: ACCOUNT_ACTIVATION_EMAIL_BODY_TEMPLATE

   A ``path`` to a plain-text template used to render activation email body.

   This setting is optional, and a default of
   ``registration/activation_email.txt`` will be used if not specified.

   A ``TemplateSyntaxError`` will be raised if the specified template could not
   be found.

   Used by:

   * :ref:`The two-step HMAC activation workflow <hmac-workflow>`

   * :ref:`The model-based activation workflow <model-workflow>`


.. data:: ACCOUNT_ACTIVATION_EMAIL_HTML_BODY_TEMPLATE

   A ``path`` to an optional alternative HTML template used to render
   activation email body.

   This setting is optional, and a default of
   ``registration/activation_email.html`` will be used if not specified.

   If the specified template could not be found, no HTML alternative email body
   will be sent.

   Used by:

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
   to be kept secret; see ref:`the note about this salt value and
   security <salt-security>` for details.

   Used by:

   * :ref:`The two-step HMAC activation workflow <hmac-workflow>`
