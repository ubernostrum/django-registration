.. _index:

django-registration |release|
=============================

``django-registration`` is an extensible application providing user
registration functionality for `Django <https://www.djangoproject.com/>`_
sites.

It has built-in support for:

* User registration with the default Django user model

* User registration with many custom user models

* Two-step (email an activation link) registration

* One-step (register and be immediately logged in) registration

And is designed to be extensible to support use cases beyond what's
built in.

For example, to enable one-step registration, you'd add
``"django_registration"`` to your Django ``INSTALLED_APPS`` setting,
then add the following to your site's root URLconfig:

.. code-block:: python

   from django.urls import include, path

   urlpatterns = [
       # Other URL patterns ...
       path("accounts/", include("django_registration.backends.one_step.urls")),
       path("accounts/", include("django.contrib.auth.urls")),
       # More URL patterns ...
   ]

And create a few templates (see :ref:`the quick start guide <quickstart>` for
full details).


Documentation contents
----------------------

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
   changelog
   faq

.. seealso::

   * `Django's authentication documentation
     <https://docs.djangoproject.com/en/stable/topics/auth/>`_. Django's
     authentication system is used by ``django-registration``'s default
     configuration.
