.. _quickstart:

Quick start guide
=================

First you'll need to have Django and ``django-registration``
installed; for details on that, see :ref:`the installation guide
<install>`.

The next steps will depend on which registration workflow you'd like
to use. There are three workflows built in to ``django-registration``;
one is included largely for backwards compatibility with older
releases, while the other two are recommended for new
installations. Those two are:

* :ref:`The HMAC activation workflow <hmac-workflow>`, which
  implements a two-step process: a user signs up, then is emailed an
  activation link and must click it to activate the account.

* :ref:`The simple one-step workflow <simple-workflow>`, in which a
  user simply signs up and their account is immediately active and
  logged in.

The guide below covers use of these two workflows.

Before proceeding with either of the recommended built-in workflows,
you'll need to ensure ``django.contrib.auth`` has been installed (by
adding it to ``INSTALLED_APPS`` and running ``manage.py migrate`` to
install needed database tables). Also, if you're making use of `a
custom user model
<https://docs.djangoproject.com/en/stable/topics/auth/customizing/#substituting-a-custom-user-model>`_,
you'll probably want to pause and read :ref:`the custom user
compatibility guide <custom-user>` before using
``django-registration``.


Configuring the HMAC activation workflow
----------------------------------------

The configuration process for using the HMAC activation workflow is
straightforward: you'll need to specify a couple of settings, connect
some URLs and create a few templates.


Required settings
~~~~~~~~~~~~~~~~~

Begin by adding the following setting to your Django settings file:

:data:`~django.conf.settings.ACCOUNT_ACTIVATION_DAYS`
    This is the number of days users will have to activate their
    accounts after registering. If a user does not activate within
    that period, the account will remain permanently inactive unless a
    site administrator manually activates it.

For example, you might have something like the following in your
Django settings file::

    ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.

You'll also need to have ``django.contrib.auth`` in your
``INSTALLED_APPS`` setting, since all of the registration workflows in
``django-registration`` make use of it.

.. warning:: You should **not** add ``registration`` to your
   ``INSTALLED_APPS`` setting if you're following this document. This
   section is walking you through setup of the :ref:`the HMAC
   activation workflow <hmac-workflow>`, and that does not make use of
   any custom models or other features which require ``registration``
   to be in ``INSTALLED_APPS``. Only add ``registration`` to your
   ``INSTALLED_APPS`` setting if you're using :ref:`the model-based
   activation workflow <model-workflow>`, or something derived from
   it.


Setting up URLs
~~~~~~~~~~~~~~~

Each bundled registration workflow in ``django-registration`` includes
a Django URLconf which sets up URL patterns for :ref:`the views in
django-registration <views>`, as well as several useful views in
``django.contrib.auth`` (e.g., login, logout, password
change/reset). The URLconf for the HMAC activation workflow can be
found at ``registration.backends.hmac.urls``, and so can simply be
included in your project's root URL configuration. For example, to
place the URLs under the prefix ``/accounts/``, you could add the
following to your project's root URLconf:

.. code-block:: python

   from django.conf.urls import include, url

   urlpatterns = [
       # Other URL patterns ...
       url(r'^accounts/', include('registration.backends.hmac.urls')),
       # More URL patterns ...
   ]

Users would then be able to register by visiting the URL
``/accounts/register/``, log in (once activated) at
``/accounts/login/``, etc.

Another ``URLConf`` is also provided -- at ``registration.auth_urls``
-- which just handles the Django auth views, should you want to put
those at a different location.


.. _default-templates:

Required templates
~~~~~~~~~~~~~~~~~~

You will also need to create several templates required by
``django-registration``, and possibly additional templates required by
views in ``django.contrib.auth``. The templates required by
``django-registration`` are as follows; note that, with the exception
of the templates used for account activation emails, all of these are
rendered using a ``RequestContext`` and so will also receive any
additional variables provided by `context processors
<https://docs.djangoproject.com/en/stable/ref/templates/api/#id1>`_.

**registration/registration_form.html**

Used to show the form users will fill out to register. By default, has
the following context:

``form``
    The registration form. This will likely be a subclass of
    :class:`~registration.forms.RegistrationForm`; consult `Django's
    forms documentation
    <https://docs.djangoproject.com/en/stable/topics/forms/>`_ for
    information on how to display this in a template.

**registration/registration_complete.html**

Used after successful completion of the registration form. This
template has no context variables of its own, and should simply inform
the user that an email containing account-activation information has
been sent.

**registration/activate.html**

Used if account activation fails. With the default setup, has the following context:

``activation_key``
    The activation key used during the activation attempt.

**registration/activation_complete.html**

Used after successful account activation. This template has no context
variables of its own, and should simply inform the user that their
account is now active.

**registration/activation_email_subject.txt**

Used to generate the subject line of the activation email. Because the
subject line of an email must be a single line of text, any output
from this template will be forcibly condensed to a single line before
being used. This template has the following context:

``activation_key``
    The activation key for the new account.

``expiration_days``
    The number of days remaining during which the account may be
    activated.

``site``
    An object representing the site on which the user registered;
    depending on whether ``django.contrib.sites`` is installed, this
    may be an instance of either ``django.contrib.sites.models.Site``
    (if the sites application is installed) or
    ``django.contrib.sites.requests.RequestSite`` (if not). Consult
    `the documentation for the Django sites framework
    <https://docs.djangoproject.com/en/stable/ref/contrib/sites/>`_ for
    details regarding these objects' interfaces.

**registration/activation_email.txt**

Used to generate the body of the activation email. Should display a
link the user can click to activate the account. This template has the
following context:

``activation_key``
    The activation key for the new account.

``expiration_days``
    The number of days remaining during which the account may be
    activated.

``site``
    An object representing the site on which the user registered;
    depending on whether ``django.contrib.sites`` is installed, this
    may be an instance of either ``django.contrib.sites.models.Site``
    (if the sites application is installed) or
    ``django.contrib.sites.requests.RequestSite`` (if not). Consult
    `the documentation for the Django sites framework
    <https://docs.djangoproject.com/en/stable/ref/contrib/sites/>`_ for
    details regarding these objects.

Note that the templates used to generate the account activation email
use the extension ``.txt``, not ``.html``. Due to widespread antipathy
toward and interoperability problems with HTML email,
``django-registration`` defaults to plain-text email, and so these
templates should simply output plain text rather than HTML.

To make use of the views from ``django.contrib.auth`` (which are set
up for you by the default URLconf mentioned above), you will also need
to create the templates required by those views. Consult `the
documentation for Django's authentication system
<https://docs.djangoproject.com/en/stable/topics/auth/>`_ for details
regarding these templates.


Configuring the simple one-step workflow
--------------------------------------------

Also included is a simpler, :ref:`one-step registration workflow
<simple-workflow>`, where a user signs up and their account is
immediately active and logged in.

The simple workflow does not require any models other than those
provided by Django's own authentication system, so only
``django.contrib.auth`` needs to be in your ``INSTALLED_APPS``
setting.

You will need to configure URLs to use the simple workflow; the
easiest way is to simply ``include()`` the URLconf
``registration.backends.simple.urls`` in your root URLconf. For
example, to place the URLs under the prefix ``/accounts/`` in your URL
structure:

.. code-block:: python

   from django.conf.urls import include, url

   urlpatterns = [
       # Other URL patterns ...
       url(r'^accounts/', include('registration.simple.hmac.urls')),
       # More URL patterns ...
   ]

Users could then register accounts by visiting the URL
``/accounts/register/``.

This URLconf will also configure the appropriate URLs for the rest of
the built-in ``django.contrib.auth`` views (log in, log out, password
reset, etc.).

Finally, you will need to create one template:
``registration/registration_form.html``. See :ref:`the list of
templates above <default-templates>` for details of this template's
context.
