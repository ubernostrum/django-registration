.. _upgrade:


Upgrading from previous versions
================================

Prior to |version|, the last widely-deployed release of
``django-registration`` was 0.8; a 1.0 release was published, and
|version| is backwards-compatible with it, but appears not to have
seen wide adoption. As such, this guide covers the process of
upgrading from ``django-registration`` 0.8.


Backends are now class-based views
----------------------------------

In ``django-registration`` 0.8, a registration workflow was
implemented as a class with specific methods for the various steps of
the registration process. In ``django-registration`` |version|, a
registration workflow is implemented as one or more class-based views.

In general, the required changes to implement a 0.8 registration
workflow in ``django-registration`` |version| is:

+-------------------------------------------------------------+------------------------------------------------------------------+
| 0.8 backend class implementation                            | |version| view subclass implementation                           |
+=============================================================+==================================================================+
| Backend class implementing ``register()``                   | :meth:`registration.views.RegistrationView.register`             |
+-------------------------------------------------------------+------------------------------------------------------------------+
| Backend class implementing ``activate()``                   | :meth:`registration.views.ActivationView.activate`               |
+-------------------------------------------------------------+------------------------------------------------------------------+
| Backend class implementing ``registration_allowed()``       | :meth:`registration.views.RegistrationView.registration_allowed` |
+-------------------------------------------------------------+------------------------------------------------------------------+
| Backend class implementing ``get_form_class()``             | :meth:`registration.views.RegistrationView.get_form_class()`     |
+-------------------------------------------------------------+------------------------------------------------------------------+
| Backend class implementing ``post_registration_redirect()`` | :meth:`registration.views.RegistrationView.get_success_url()`    |
+-------------------------------------------------------------+------------------------------------------------------------------+
| Backend class implementing ``post_activation_redirect()``   | :meth:`registration.views.ActivationView.get_success_url()`      |
+-------------------------------------------------------------+------------------------------------------------------------------+


URLconf changes
---------------

If you were using one of the provided backends in
``django-registration`` 0.8 without modification, you will not need to
make any changes; both ``registration.backends.default.urls`` and
``registration.backends.simple.urls`` have been updated in
``django-registration`` |version| to correctly point to the new
class-based views:

+---------------------------------+---------------------------------------------------+
| 0.8 URLconf view reference      | |version| URLconf view reference                  |
+=================================+===================================================+
| ``registration.views.register`` | ``registration.views.RegistrationView.as_view()`` |
+---------------------------------+---------------------------------------------------+
| ``registration.views.activate`` | ``registration.views.ActivationView.as_view()``   |
+---------------------------------+---------------------------------------------------+

If you were passing custom arguments to the built-in registration
views, those arguments should continue to work, so long as your
URLconf is updated to refer to the new class-based views. For details
of how to pass custom arguments to class-based views, see `the Django
class-based view documentation
<https://docs.djangoproject.com/en/1.8/topics/class-based-views/#simple-usage-in-your-urlconf>`_.
