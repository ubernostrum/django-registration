.. -*-restructuredtext-*-

.. image:: https://github.com/ubernostrum/django-registration/workflows/CI/badge.svg
   :alt: CI status image
   :target: https://github.com/ubernostrum/django-registration/actions?query=workflow%3ACI

This is a user-registration application for `Django
<https://www.djangoproject.com/>`_ sites.

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

And create a few templates (see `the quick start guide
<https://django-registration.readthedocs.io/en/stable/quickstart.html>`_
for details).

For more, check out `the full documentation
<https://django-registration.readthedocs.io/>`_.
