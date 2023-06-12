.. _exceptions:
.. module:: django_registration.exceptions


Exception classes
=================

django-registration provides two base exception classes to signal errors which
occur during the signup or activation processes.

.. exception:: RegistrationError(message, code, params)

   Base exception class for all exceptions raised in django-registration. No
   code in django-registration will raise this exception directly; it serves
   solely to provide a distinguishing parent class for other errors. Arguments
   passed when the exception is raised will be stored and exposed as attributes
   of the same names on the exception object:

   :param str message: A human-readable error message.
   :param str code: A short but unique identifier used by subclasses
         to distinguish different error conditions.
   :param dict params: Arbitrary key-value data to associate with the error.


.. exception:: ActivationError(message, code, params)

   Exception class to indicate errors during account activation. Subclass of
   :exc:`RegistrationError` and inherits its attributes.
