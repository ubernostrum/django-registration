.. _exceptions:
.. module:: django_registration.exceptions


Exception classes
=================

django-registration provides two base exception classes to signal
errors which occur during the signup or activation processes.

.. class:: RegistrationError

   Base exception class for all exceptions raised in
   django-registration. No code in django-registration will raise this
   exception directly; it serves solely to provide a distinguishing
   parent class for other errors.

   .. method:: __init__(message, code, params)

      Errors can be raised with several arguments, for use by whatever
      code will catch and work with them, and which will be turned
      into attributes on the resulting exception object.

      :param message: A human-readable error message.
      :type message: ``str``
      :param code: A short but unique identifier used by subclasses to
         distinguish different error conditions.
      :type code: ``str``
      :param params: Arbitrary key-value data to associate with the error.
      :type params: ``dict``


.. class:: ActivationError

   Exception class to indicate errors during account
   activation.