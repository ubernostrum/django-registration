.. _hmac-workflow:
.. module:: registration.backends.hmac

The HMAC activation workflow
============================

The HMAC workflow, found in ``registration.backends.hmac``, implements
a two-step registration process (signup, followed by activation), but
unlike the older :ref:`model-based activation workflow
<model-workflow>` uses no models and does not store its activation
key; instead, the activation key sent to the user is a timestamped,
`HMAC
<https://en.wikipedia.org/wiki/Hash-based_message_authentication_code>`_-verified
value.

Unless you need to maintain compatibility in an existing install of
``django-registration`` which used the model-based workflow, it's
recommended you use the HMAC activation workflow for two-step signup
processes.


Behavior and configuration
--------------------------

Since this workflow does not make use of any additional models beyond
the user model (either Django's default
``django.contrib.auth.models.User``, or :ref:`a custom user model
<custom-user>`), *do not* add ``registration`` to your
``INSTALLED_APPS`` setting.

You will need to configure URLs, however. A default URLconf is
provided, which you can ``include()`` in your URL configuration; that
URLconf is ``registration.backends.hmac.urls``. For example, to place
user registration under the URL prefix ``/accounts/``, you could place
the following in your root URLconf::

    ``url(r'^accounts/', include('registration.backends.hmac.urls')),``

That URLconf also sets up the views from ``django.contrib.auth``
(login, logout, password reset, etc.), though if you want those views
at a different location, you can ``include()`` the URLconf
``registration.auth_urls`` to place only the ``django.contrib.auth``
views at a specific location in your URL hierarchy.

This workflow makes use of up to three settings:

``ACCOUNT_ACTIVATION_DAYS``
    This is the number of days users will have to activate their
    accounts after registering. Failing to activate during that period
    will leave the account inactive (and possibly subject to
    deletion). This setting is required, and must be an integer.

``REGISTRATION_OPEN``
    A boolean (either ``True`` or ``False``) indicating whether
    registration of new accounts is currently permitted. This setting
    is optional, and a default of ``True`` will be assumed if it is
    not supplied.

``REGISTRATION_SALT``
    A string used as an additional "salt" in the process of signing
    activation keys. This setting is optional, and the string
    ``"registration"`` will be used if it is not supplied. Changing
    this setting provides no additional security, and it is used
    solely as a way of namespacing HMAC usage.

By default, this workflow uses
:class:`registration.forms.RegistrationForm` as its form class for
user registration; this can be overridden by passing the keyword
argument ``form_class`` to the registration view.

Two views are provided:
``registration.backends.hmac.views.RegistrationView`` and
``registration.backends.hmac.views.ActivationView``. These
views subclass ``django-registration``'s base
:class:`~registration.views.RegistrationView` and
:class:`~registration.views.ActivationView`, respectively, and
implement the two-step registration/activation process.

Upon successful registration -- not activation -- the user will be
redirected to the URL pattern named ``registration_complete``.

Upon successful activation, the user will be redirected to the URL
pattern named ``registration_activation_complete``.

For an overview of the templates used in this workflow, and their
context variables, see :ref:`the quick start guide <quickstart>`.


How it works
------------

When a user signs up, the HMAC workflow creates a new ``User``
instance to represent the account, and sets the ``is_active`` field to
``False``. It then sends an email to the address provided during
signup, containing a link to activate the account. When the user
clicks the link, the activation view sets ``is_active`` to ``True``,
after which the user can log in.

The activation key is simply the username of the new account, signed
using `Django's cryptographic signing tools
<https://docs.djangoproject.com/en/1.8/topics/signing/>`_. The
activation process includes verification of the signature prior to
activation, as well as verifying that the user is activating within
the permitted window (as specified in the setting
``ACCOUNT_ACTIVATION_DAYS``, mentioned above), through use of Django's
``TimestampSigner``.


Comparison to the model-activation workflow
-------------------------------------------

The primary advantage of the HMAC activation workflow is that it
requires no persistent storage of the activation key. However, this
means there is no longer an automated way to differentiate accounts
which have been purposefully deactivated (for example, as a way to ban
a user) from accounts which failed to activate within a specified
window.

Since the HMAC activation workflow does not use any models, it also
does not make use of the admin interface and thus does not offer a
convenient way to re-send an activation email. Users who have
difficulty receiving the activation email can simply be manually
activated by a site administrator.

However, the reduced overhead of not needing to store the activation
key makes this generally preferable to :ref:`the model-based workflow
<model-workflow>`.


Security considerations
-----------------------

The activation key emailed to the user in the HMAC activation workflow
is a value obtained by using Django's cryptographic signing tools.

In particular, the activation key is of the form::

    username:timestamp:signature

Where ``username`` is the username of the new account, ``timestamp``
is a base62-encoded timestamp of the time the user registered, and
``signature`` is a URL-safe base64-encoded HMAC of the username and
timestamp.

Django's implementation uses the value of the ``SECRET_KEY`` setting
as the key for HMAC; additionally, it permits the specification of a
salt value which can be used to "namespace" different uses of HMAC
across a Django-powered site.

The HMAC activation workflow will use the value (a string) of the
setting ``REGISTRATION_SALT`` as the salt, defaulting to the string
``"registration"`` if that setting is not specified. This value does
*not* need to be kept secret (only ``SECRET_KEY`` does); it serves
only to ensure that other parts of a site which also produce signed
values from user input could not be used as a way to generate
activation keys for arbitrary usernames (and vice-versa).
