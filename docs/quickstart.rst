.. _quickstart:

Quick start guide
=================

First you'll need to have Django and django-registration installed; for details
on that, see :ref:`the installation guide <install>`.

The next steps will depend on which registration workflow you'd like to
use. There are two workflows built into django-registration:

* :ref:`The two-step activation workflow <activation-workflow>`, which
  implements a two-step process: a user signs up, then is emailed an activation
  link and must click it to activate the account.

* :ref:`The one-step workflow <one-step-workflow>`, in which a user signs up
  and their account is immediately active and logged in.

If you want a signup process other than what's provided by these built-in
workflows, please see the documentation for the base :ref:`view <views>` and
:ref:`form <forms>` classes, which you can subclass to implement your own
preferred user registration flow and rules. The guide below covers use of the
built-in workflows.

Regardless of which registration workflow you choose to use, you should add
`"django_registration"` to your :data:`~django.conf.settings.INSTALLED_APPS`
setting.

.. important:: **Django's authentication system must be installed**

   Before proceeding with either of the recommended built-in workflows, you'll
   need to ensure ``django.contrib.auth`` has been installed (by adding it to
   :data:`~django.conf.settings.INSTALLED_APPS` and running ``manage.py
   migrate`` to install needed database tables). Also, if you're making use of
   `a custom user model
   <https://docs.djangoproject.com/en/stable/topics/auth/customizing/#substituting-a-custom-user-model>`_,
   you'll probably want to pause and read :ref:`the custom user compatibility
   guide <custom-user>` before using django-registration.

.. note:: **Additional steps for account security**

   While django-registration does what it can to secure the user signup
   process, its scope is deliberately limited; please read :ref:`the security
   documentation <security>` for recommendations on steps to secure user
   accounts beyond what django-registration alone can do.


Configuring the two-step activation workflow
--------------------------------------------

The configuration process for using the two-step activation workflow is
straightforward: you'll need to specify a couple of settings, connect some URLs
and create a few templates.


Required settings
~~~~~~~~~~~~~~~~~

Begin by adding the following setting to your Django settings file:

:data:`~django.conf.settings.ACCOUNT_ACTIVATION_DAYS` This is the number of
    days users will have to activate their accounts after registering. If a
    user does not activate within that period, the account will remain
    permanently inactive unless a site administrator manually activates it.

For example, you might have something like the following in your Django
settings::

    ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window


Setting up URLs
~~~~~~~~~~~~~~~

Each bundled registration workflow in django-registration includes a Django
URLconf which sets up URL patterns for :ref:`the views in django-registration
<views>`. The URLconf for the two-step activation workflow can be found at
``django_registration.backends.activation.urls``. For example, to place the
registration URLs under the prefix ``/accounts/``, you could add the following
to your project's root URLconf:

.. code-block:: python

   from django.urls import include, path

   urlpatterns = [
       # Other URL patterns ...
       path('accounts/', include('django_registration.backends.activation.urls')),
       path('accounts/', include('django.contrib.auth.urls')),
       # More URL patterns ...
   ]

Users would then be able to register by visiting the URL
``/accounts/register/``, log in (once activated) at ``/accounts/login/``, etc.

The sample URL configuration above also sets up the built-in auth views
included in Django (login, logout, password reset, etc.) via the
``django.contrib.auth.urls`` URLconf.

The following URL names are defined by
``django_registration.backends.activation.urls``:

* ``django_registration_register`` is the account-registration view.

* ``django_registration_complete`` is the post-registration success message.

* ``django_registration_activate`` is the account-activation view.

* ``django_registration_activation_complete`` is the post-activation success
  message.

* ``django_registration_disallowed`` is a message indicating registration is not
  currently permitted.


.. _default-templates:

Required templates
~~~~~~~~~~~~~~~~~~

You will also need to create several templates required by django-registration,
and possibly additional templates required by views in
``django.contrib.auth``. The templates required by django-registration are as
follows; note that, with the exception of the templates used for account
activation emails, all of these are rendered using a
:class:`~django.template.RequestContext` and so will also receive any
additional variables provided by `context processors
<https://docs.djangoproject.com/en/stable/ref/templates/api/#id1>`_.


.. _default-form-template:

``django_registration/registration_form.html``
``````````````````````````````````````````````

Used to show the form users will fill out to register. By default, has the
following context:

``form``
    The registration form. This will likely be a subclass of
    :class:`~django_registration.forms.RegistrationForm`; consult
    `Django's forms documentation
    <https://docs.djangoproject.com/en/stable/topics/forms/>`_ for
    information on how to display this in a template.


``django_registration/registration_complete.html``
``````````````````````````````````````````````````

Used after successful completion of the registration form. This template has no
context variables of its own, and should inform the user that an email
containing account-activation information has been sent.


``django_registration/registration_closed.html``
````````````````````````````````````````````````

Used when registration of new user accounts is disabled. This template has no
context variables of its own.


``django_registration/activation_failed.html``
``````````````````````````````````````````````

Used if account activation fails. Has the following context:

``activation_error``
    A :class:`dict` containing the information supplied to the
    :exc:`~django_registration.exceptions.ActivationError` which occurred
    during activation. See the documentation for that exception for a
    description of the keys, and the documentation for
    :class:`~django_registration.backends.activation.views.ActivationView` for
    the specific values used in different failure situations.


``django_registration/activation_complete.html``
````````````````````````````````````````````````

Used after successful account activation. This template has no context
variables of its own, and should inform the user that their account is now
active.


``django_registration/activation_email_subject.txt``
````````````````````````````````````````````````````

Used to generate the subject line of the activation email. Because the subject
line of an email must be a single line of text, any output from this template
will be forcibly condensed to a single line before being used. This template
has the following context:

``activation_key``
    The activation key for the new account, as a string.

``expiration_days``
    The number of days remaining during which the account may be activated, as
    an integer.

``request``
    The :class:`~django.http.HttpRequest` object representing the request in
    which the user registered.

``scheme``
    The protocol scheme used during registration, as a string; will be either
    ``'http'`` or ``'https'``.

``site``
    An object representing the site on which the user registered; depending on
    whether ``django.contrib.sites`` is installed, this may be an instance of
    either :class:`django.contrib.sites.models.Site` (if the sites application
    is installed) or :class:`django.contrib.sites.requests.RequestSite` (if
    not). Consult `the documentation for the Django sites framework
    <https://docs.djangoproject.com/en/stable/ref/contrib/sites/>`_ for details
    regarding these objects' interfaces.

``user``
    The newly-created user object.


``django_registration/activation_email_body.txt``
`````````````````````````````````````````````````

Used to generate the body of the activation email. Should display a link the
user can click to activate the account. This template has the following
context:

``activation_key``
    The activation key for the new account, as a string.

``expiration_days``
    The number of days remaining during which the account may be activated, as
    an integer.

``request``
    The :class:`~django.http.HttpRequest` object representing the request in
    which the user registered.

``scheme``
    The protocol scheme used during registration, as a string; will be either
    `'http'` or `'https'`.

``site``
    An object representing the site on which the user registered; depending on
    whether `django.contrib.sites` is installed, this may be an instance of
    either :class:`django.contrib.sites.models.Site` (if the sites application
    is installed) or :class:`django.contrib.sites.requests.RequestSite` (if
    not). Consult `the documentation for the Django sites framework
    <https://docs.djangoproject.com/en/stable/ref/contrib/sites/>`_ for details
    regarding these objects.

``user``
    The newly-created user object.

Note that the templates used to generate the account activation email use the
extension ``.txt``, not ``.html``. Due to widespread antipathy toward and
interoperability problems with HTML email, django-registration produces
plain-text email, and so these templates should output plain text rather than
HTML.

To make use of the views from ``django.contrib.auth`` (which are set up for you
by the example URL configuration above), you will also need to create the
templates required by those views. Consult `the documentation for Django's
authentication system <https://docs.djangoproject.com/en/stable/topics/auth/>`_
for details regarding these templates.


Configuring the one-step workflow
--------------------------------------------

Also included is a :ref:`one-step registration workflow <one-step-workflow>`,
where a user signs up and their account is immediately active and logged in.

You will need to configure URLs to use the one-step workflow; the easiest way
is to :func:`~django.urls.include` the URLconf
`django_registration.backends.one_step.urls` somewhere in your URL
configuration. For example, to place the URLs under the prefix `/accounts/` in
your URL structure:

.. code-block:: python

   from django.urls import include, path

   urlpatterns = [
       # Other URL patterns ...
       path('accounts/', include('django_registration.backends.one_step.urls')),
       path('accounts/', include('django.contrib.auth.urls')),
       # More URL patterns ...
   ]

Users could then register accounts by visiting the URL ``/accounts/register/``.

The following URL names are defined by
``django_registration.backends.one_step.urls``:

* ``django_registration_register`` is the account-registration view.

* ``django_registration_complete`` is the post-registration success message.

* ``django_registration_disallowed`` is a message indicating registration is not
  currently permitted.

This URLconf will also configure the appropriate URLs for the rest of the
built-in `django.contrib.auth` views (log in, log out, password reset, etc.).

Finally, you will need to create following templates:

* ``django_registration/registration_form.html``
* ``django_registration/registration_complete.html``
* ``django_registration/registration_closed.html``

See :ref:`the documentation above <default-form-template>` for details of these
templates.

To make use of the views from ``django.contrib.auth`` (which are set up for you
by the example URL configuration above), you will also need to create the
templates required by those views. Consult `the documentation for Django's
authentication system <https://docs.djangoproject.com/en/stable/topics/auth/>`_
for details regarding these templates.
