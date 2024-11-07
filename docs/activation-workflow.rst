.. _activation-workflow:
.. module:: django_registration.backends.activation

The two-step activation workflow
================================

The two-step activation workflow, found in
``django_registration.backends.activation``, implements a two-step registration
process: a user signs up, an inactive account is created, and an email is sent
containing an activation link which must be clicked to make the account active.


Behavior and configuration
--------------------------

A default URLconf is provided, which you can :func:`~django.urls.include` in
your URL configuration; that URLconf is
``django_registration.backends.activation.urls``. For example, to place user
registration under the URL prefix ``/accounts/``, you could place the following
in your root URLconf:

.. code-block:: python

   from django.urls import include, path

   urlpatterns = [
       # Other URL patterns ...
       path('accounts/', include('django_registration.backends.activation.urls')),
       path('accounts/', include('django.contrib.auth.urls')),
       # More URL patterns ...
   ]

That also sets up the views from ``django.contrib.auth`` (login, logout, password
reset, etc.).

This workflow makes use of up to three settings (click for details on each):

* :data:`~django.conf.settings.ACCOUNT_ACTIVATION_DAYS`

* :data:`~django.conf.settings.REGISTRATION_OPEN`

* :data:`~django.conf.settings.REGISTRATION_SALT` (see also :ref:`note below
  <salt-security>`)

By default, this workflow uses
:class:`~django_registration.forms.RegistrationForm` as its form class for user
registration; this can be overridden by passing the keyword argument
``form_class`` to the registration view.

Forms
-----

.. currentmodule:: django_registration.backends.activation.forms

.. autoclass:: ActivationForm


Views
-----

.. currentmodule:: django_registration.backends.activation.views

Two views are provided to implement the signup/activation process. These
subclass :ref:`the base views of django-registration <views>`, so anything that
can be overridden/customized there can equally be overridden/customized
here. There are some additional customization points specific to this
implementation, which are listed below.

For an overview of the templates used by these views (other than those
specified below), and their context variables, see :ref:`the quick start guide
<default-templates>`.


.. autoclass:: RegistrationView

.. autoclass:: ActivationView


How it works
------------

When a user signs up, the activation workflow creates a new user instance to
represent the account, and sets the ``is_active`` field to :data:`False`. It then
sends an email to the address provided during signup, containing a link to
activate the account. When the user clicks the link, the activation view sets
``is_active`` to :data:`True`, after which the user can log in.

The activation key is the username of the new account, signed using `Django's
cryptographic signing tools
<https://docs.djangoproject.com/en/stable/topics/signing/>`_ (specifically,
:func:`~django.core.signing.dumps()` is used, to produce a guaranteed-URL-safe
value). The activation process includes verification of the signature prior to
activation, as well as verifying that the user is activating within the
permitted window (as specified in the setting
:data:`~django.conf.settings.ACCOUNT_ACTIVATION_DAYS`, mentioned above),
through use of Django's :class:`~django.core.signing.TimestampSigner`.


Security considerations
-----------------------

The activation key emailed to the user in the activation workflow is a value
obtained by using Django's cryptographic signing tools. The activation key is
of the form::

    encoded_username:timestamp:signature

where ``encoded_username`` is the username of the new account, ``timestamp`` is the
timestamp of the time the user registered, and ``signature`` is an HMAC of the
username and timestamp. The username and HMAC will be URL-safe base64 encoded;
the timestamp will be base62 encoded.

Django's implementation uses the value of the
:data:`~django.conf.settings.SECRET_KEY` setting as the key for
HMAC. Additionally, it permits the specification of a salt value which can be
used to "namespace" different uses of HMAC across a Django-powered site.

.. _salt-security:

The activation workflow will use the value (a string) of the setting
:data:`~django.conf.settings.REGISTRATION_SALT` as the salt, defaulting to the
string ``"registration"`` if that setting is not specified. This value does *not*
need to be kept secret (only :data:`~django.conf.settings.SECRET_KEY` does); it
serves only to ensure that other parts of a site which also produce signed
values from user input could not be used as a way to generate activation keys
for arbitrary usernames (and vice-versa).
