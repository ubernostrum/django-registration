.. _forms:
.. module:: django_registration.forms

Form classes
============

Several form classes are provided with ``django-registration``, covering common
cases for gathering account information and implementing common constraints for
user registration. These forms were designed with ``django-registration``'s
built-in registration workflows in mind, but may also be useful in other
situations.

.. autoclass:: RegistrationForm

   .. automethod:: clean
   .. automethod:: save


.. autoclass:: RegistrationFormTermsOfService
.. autoclass:: RegistrationFormUniqueEmail
.. autoclass:: BaseRegistrationForm
