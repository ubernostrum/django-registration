.. _index:

django-registration |release|
=============================

django-registration is an extensible application providing user registration
functionality for `Django <https://www.djangoproject.com/>`_-powered Web sites.

Although nearly all aspects of the registration process are customizable,
out-of-the-box support is provided for two common use cases:

* Two-phase registration, consisting of initial signup followed by a
  confirmation email with instructions for activating the new account.

* One-phase registration, where a user signs up and is immediately active and
  logged in.

To get up and running quickly, :ref:`install django-registration <install>`,
then read :ref:`the quick start guide <quickstart>`, which describes the steps
necessary to configure django-registration for the built-in workflows. For more
detailed information, including how to customize the registration process (and
support for alternate registration systems), read through the documentation
listed below.


.. toctree::
   :caption: Installation and configuration
   :maxdepth: 1

   install
   quickstart

.. toctree::
   :caption: Built-in registration workflows
   :maxdepth: 1

   activation-workflow
   one-step-workflow

.. toctree::
   :caption: For developers
   :maxdepth: 1

   views
   forms
   custom-user
   validators
   exceptions
   settings
   signals
   deprecations

.. toctree::
   :caption: Other documentation
   :maxdepth: 1

   security
   upgrade
   faq

.. seealso::

   * `Django's authentication documentation
     <https://docs.djangoproject.com/en/stable/topics/auth/>`_. Django's
     authentication system is used by django-registration's default
     configuration.
