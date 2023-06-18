.. _one-step-workflow:
.. module:: django_registration.backends.one_step

The one-step workflow
=====================

As an alternative to :ref:`the two-step (registration and activation) workflow
<activation-workflow>`, django-registration bundles a one-step registration
workflow in ``django_registration.backends.one_step``. This workflow consists of
as few steps as possible:

1. A user signs up by filling out a registration form.

2. The user's account is created and is active immediately, with no
   intermediate confirmation or activation step.

3. The new user is logged in immediately.


Configuration
-------------

To use this workflow, include the URLconf
``django_registration.backends.one_step.urls`` somewhere in your site's own URL
configuration. For example:

.. code-block:: python

   from django.urls import include, path

   urlpatterns = [
       # Other URL patterns ...
       path('accounts/', include('django_registration.backends.one_step.urls')),
       path('accounts/', include('django.contrib.auth.urls')),
       # More URL patterns ...
   ]

To control whether registration of new accounts is allowed, you can specify the
setting :data:`~django.conf.settings.REGISTRATION_OPEN`.

Upon successful registration, the user will be redirected to the site's home
page -- the URL ``/``. This can be changed by subclassing
:class:`django_registration.backends.one_step.views.RegistrationView` and
overriding the method
:meth:`~django_registration.views.RegistrationView.get_success_url` or setting
the attribute
:attr:`~django_registration.views.RegistrationView.success_url`. You can also
do this in a URLconf. For example:

.. code-block:: python

   from django.urls import include, path

   from django_registration.backends.one_step.views import RegistrationView

   urlpatterns = [
       # Other URL patterns ...
       path('accounts/register/',
           RegistrationView.as_view(success_url='/profile/'),
	   name='django_registration_register'),
       path('accounts/', include('django_registration.backends.one_step.urls')),
       path('accounts/', include('django.contrib.auth.urls')),
       # More URL patterns ...
   ]

The default form class used for account registration will be
:class:`django_registration.forms.RegistrationForm`, although this can be
overridden by supplying a custom URL pattern for the registration view and
passing the keyword argument ``form_class``, or by subclassing
:class:`django_registration.backends.one_step.views.RegistrationView` and
either overriding
:attr:`~django_registration.views.RegistrationView.form_class` or implementing
:meth:`~django_registration.views.RegistrationView.get_form_class()`, and
specifying the custom subclass in your URL patterns.


Templates
---------

The one-step workflow uses two templates:

* ``django_registration/registration_form.html``.
* ``django_registration/registration_closed.html``

See :ref:`the quick start guide <default-form-template>` for details of these
templates.
