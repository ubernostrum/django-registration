.. _simple-workflow:
.. module:: registration.backends.simple

The "simple" (one-step) workflow
================================

As an alternative to the :ref:`HMAC <hmac-workflow>` and
:ref:`model-based <model-workflow>` two-step (registration and
activation) systems, ``django-registration`` bundles a one-step
registration system in ``registration.backend.simple``. This workflow
is deliberately as simple as possible:

1. A user signs up by filling out a registration form.

2. The user's account is created and is active immediately, with no
   intermediate confirmation or activation step.

3. The new user is logged in immediately.


Configuration
-------------

To use this workflow, simply include the URLconf
``registration.backends.simple.urls`` somewhere in your site's own URL
configuration. For example::

    url(r'^accounts/', include('registration.backends.simple.urls')),

No additional settings are required, but one optional setting is
supported:

``REGISTRATION_OPEN``
    A boolean (either ``True`` or ``False``) indicating whether
    registration of new accounts is currently permitted. A default of
    ``True`` will be assumed if this setting is not supplied.

Upon successful registration, the user will be redirected to the
site's home page -- the URL ``/``. This can be changed by subclassing
``registration.backends.simple.views.RegistrationView`` and overriding
the method ``get_success_url()``.

The default form class used for account registration will be
:class:`registration.forms.RegistrationForm`, although this can be
overridden by supplying a custom URL pattern for the registration view
and passing the keyword argument ``form_class``, or by subclassing
``registration.backends.simple.views.RegistrationView`` and either
overriding ``form_class`` or implementing
:meth:`~registration.views.RegistrationView.get_form_class()`, and
specifying the custom subclass in your URL patterns.


Templates
---------

The one-step workflow uses only one custom template:

**registration/registration_form.html**

Used to show the form users will fill out to register. By default, has
the following context:

``form``
    The registration form. This will be an instance of some subclass
    of ``django.forms.Form``; consult `Django's forms documentation
    <https://docs.djangoproject.com/en/1.8/topics/forms/>`_ for
    information on how to display this in a template.


