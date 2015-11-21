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
the following in your root URLconf:

.. code-block:: python

   from django.conf.urls import include, url

   urlpatterns = [
       # Other URL patterns ...
       url(r'^accounts/', include('registration.backends.hmac.urls')),
       # More URL patterns ...
   ]

That URLconf also sets up the views from ``django.contrib.auth``
(login, logout, password reset, etc.), though if you want those views
at a different location, you can ``include()`` the URLconf
``registration.auth_urls`` to place only the ``django.contrib.auth``
views at a specific location in your URL hierarchy.

.. note:: **URL patterns for activation**

   Although the actual value used in the activation key is the new
   user account's username, the URL pattern for
   :class:`~registration.views.backends.hmac.ActivationView` does not
   need to match all possible legal characters in a username. The
   activation key that will be sent to the user (and thus matched in
   the URL) is produced by ``django.core.signing.dumps()``, which
   base64-encodes its output. Thus, the only characters this pattern
   needs to match are those from `the URL-safe base64 alphabet
   <http://tools.ietf.org/html/rfc4648#section-5>`_, plus the colon
   ("``:``") which is used as a separator.

   The default URL pattern for the activation view in
   ``registration.backends.hmac.urls`` handles this for you.

This workflow makes use of up to three settings:

* :data:`~django.conf.settings.ACCOUNT_ACTIVATION_DAYS`

* :data:`~django.conf.settings.REGISTRATION_OPEN`

* :data:`~django.conf.settings.REGISTRATION_SALT`

By default, this workflow uses
:class:`registration.forms.RegistrationForm` as its form class for
user registration; this can be overridden by passing the keyword
argument ``form_class`` to the registration view.


Views
-----

.. currentmodule:: registration.backends.hmac.views

Two views are provided to implement the signup/activation
process. These subclass :ref:`the base views of django-registration
<views>`, so anything that can be overridden/customized there can
equally be overridden/customized here. There are some additional
customization points specific to the HMAC implementation, which are
listed below.

For an overview of the templates used by these views (other than those
specified below), and their context variables, see :ref:`the quick
start guide <quickstart>`.


.. class:: RegistrationView

   A subclass of :class:`registration.views.RegistrationView`
   implementing the signup portion of this workflow.

   Important customization points unique to this class are:

   .. method:: create_inactive_user(form)

      Creates and returns an inactive user account, and calls
      :meth:`send_activation_email()` to send the email with the
      activation key. The argument ``form`` is a valid registration
      form instance passed from
      :meth:`~registration.views.RegistrationView.register()`.

   .. method:: get_activation_key(user)

      Given an instance of the user model, generates and returns an
      activation key (a string) for that user account.

   .. method:: get_email_context(activation_key)

      Returns a dictionary of values to be used as template context
      when generating the activation email.

   .. method:: send_activation_email(user)

      Given an inactive user account, generates and sends the
      activation email for that account.

   .. attribute:: email_body_template

      A string specifying the template to use for the body of the
      activation email. Default is
      ``"registration/activation_email.txt"``.

   .. attribute:: email_subject_template

      A string specifying the template to use for the subject of the
      activation email. Default is
      ``"registration/activation_email_subject.txt"``. Note that, to
      avoid header-injection vulnerabilities, the result of rendering
      this template will be forced into a single line of text,
      stripping newline characters.

.. class:: ActivationView

   A subclass of :class:`registration.views.ActivationView`
   implementing the activation portion of this workflow.

   Important customization points unique to this class are:

   .. method:: get_user(username)

      Given a username (determined by the activation key), look up and
      return the corresponding instance of the user model. Returns
      ``None`` if no such instance exists. In the base implementation,
      will include ``is_active=False`` in the query to avoid
      re-activation of already-active accounts.

   .. method:: validate_key(activation_key)

      Given the activation key, verifies that it carries a valid
      signature and a timestamp no older than the number of days
      specified in the setting ``ACCOUNT_ACTIVATION_DAYS``, and
      returns the username from the activation key. Returns ``None``
      if the activation key has an invalid signature or if the
      timestamp is too old.



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
<https://docs.djangoproject.com/en/stable/topics/signing/>`_
(specifically, ``signing.dumps()`` is used, to produce a
guaranteed-URL-safe value). The activation process includes
verification of the signature prior to activation, as well as
verifying that the user is activating within the permitted window (as
specified in the setting ``ACCOUNT_ACTIVATION_DAYS``, mentioned
above), through use of Django's ``TimestampSigner``.


Comparison to the model-activation workflow
-------------------------------------------

The primary advantage of the HMAC activation workflow is that it
requires no persistent storage of the activation key. However, this
means there is no longer an automated way to differentiate accounts
which have been purposefully deactivated (for example, as a way to ban
a user) from accounts which failed to activate within a specified
window. Additionally, it is possible a user could, if manually
deactivated, re-activate their account if still within the activation
window; for this reason, when using the ``is_active`` field to "ban" a
user, it is best to also set the user's password to an unusable value
(i.e., by calling `set_unusable_password()
<https://docs.djangoproject.com/en/stable/ref/contrib/auth/#django.contrib.auth.models.User.set_unusable_password>`_
for that user). Calling ``set_unusable_password()`` will also make it
easier to query for manually-deactivated users, as their passwords
will (when using Django's default ``User`` implementation) begin with
the exclamation mark (``!``) character.

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

    encoded_username:timestamp:signature

Where ``encoded_username`` is the username of the new account,
(URL-safe) base64-encoded, ``timestamp`` is a base62-encoded timestamp
of the time the user registered, and ``signature`` is a (URL-safe)
base64-encoded HMAC of the username and timestamp.

Django's implementation uses the value of the ``SECRET_KEY`` setting
as the key for HMAC; additionally, it permits the specification of a
salt value which can be used to "namespace" different uses of HMAC
across a Django-powered site.

The HMAC activation workflow will use the value (a string) of the
setting :data:`~django.conf.settings.REGISTRATION_SALT` as the salt,
defaulting to the string ``"registration"`` if that setting is not
specified. This value does *not* need to be kept secret (only
``SECRET_KEY`` does); it serves only to ensure that other parts of a
site which also produce signed values from user input could not be
used as a way to generate activation keys for arbitrary usernames (and
vice-versa).
