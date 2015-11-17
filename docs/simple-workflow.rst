.. _simple-workflow:
.. module:: registration.backends.simple

The simple one-step workflow
============================

As an alternative to the :ref:`HMAC <hmac-workflow>` and
:ref:`model-based <model-workflow>` two-step (registration and
activation) workflows, ``django-registration`` bundles a one-step
registration workflow in ``registration.backends.simple``. This
workflow is deliberately as simple as possible:

1. A user signs up by filling out a registration form.

2. The user's account is created and is active immediately, with no
   intermediate confirmation or activation step.

3. The new user is logged in immediately.


Configuration
-------------

To use this workflow, simply include the URLconf
``registration.backends.simple.urls`` somewhere in your site's own URL
configuration. For example:

.. code-block:: python

   from django.conf.urls import include, url

   urlpatterns = [
       # Other URL patterns ...
       url(r'^accounts/', include('registration.backends.simple.urls')),
       # More URL patterns ...
   ]

To control whether registration of new accounts is allowed, you can
specify the setting :data:`~django.conf.settings.REGISTRATION_OPEN`.

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
    The registration form. This will likely be a subclass of
    :class:`~registration.forms.RegistrationForm`; consult `Django's
    forms documentation
    <https://docs.djangoproject.com/en/stable/topics/forms/>`_ for
    information on how to display this in a template.
