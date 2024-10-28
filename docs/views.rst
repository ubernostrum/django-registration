.. _views:
.. module:: django_registration.views

Base view classes
=================

In order to allow flexibility in customizing and supporting different
workflows, django-registration makes use of Django's support for `class-based
views
<https://docs.djangoproject.com/en/stable/topics/class-based-views/>`_. Included
in django-registration are two base classes which can be subclassed to
implement many types of registration workflows.

The built-in workflows in django-registration provide their own subclasses of
these views, and the documentation for those workflows will indicate
customization points specific to those subclasses. The following reference
covers useful attributes and methods of the base classes, for use in writing
your own custom registration workflows.

.. autoclass:: RegistrationView


.. autoclass:: ActivationView
