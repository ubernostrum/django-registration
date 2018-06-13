.. _upgrade:


Upgrading from previous versions
================================

The current release series of django-registration is the 3.x series,
which is not backwards-compatible with the django-registration 2.x
release series.


Module renaming
~~~~~~~~~~~~~~~

Prior to 3.x, django-registration installed a Python module named
``registration``. To avoid silent incompatibilities, and to conform to
more recent best practices, django-registration 3.x now installs a
module named ``django_registration``. Attempts to import from the
``registration`` module will immediately fail with ``ImportError``.

Many installations will be able to adapt by replacing references to
``registration`` with references to ``django_registration``.


Removal of model-based workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The two-step model-based signup workflow, which has been present since
the first public release of django-registration in 2007, has now been
removed. In its place, it is recommended that you use :ref:`the
two-step HMAC workflow <hmac-workflow>` instead, as that workflow
requires no server-side storage of additional data beyond the user
account itself.


Renaming of one-step workflow
-----------------------------

:ref:`The one-step workflow <one-step-workflow>` was previously found
at ``registration.backends.simple``; it has been renamed and is now
found at ``registration.backends.one_step``.


Removal of auth URLs
~~~~~~~~~~~~~~~~~~~~

Prior to 3.x, django-registration's default URLconf modules for its
built-in workflows would attempt to include the Django auth views
(login, logout, password reset, etc.) for you. This became untenable
with the rewrite of Django's auth views to be class-based, as it
required detecting the set of auth views and choosing a set of URL
patterns at runtime.

As a result, auth views are no longer automatically configured for
you; if you want them, ``include()`` the URLconf
``django.contrib.auth.urls`` at a location of your choosing.


Distinguishing activation failure conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prior to 3.x, failures to activate a user account (in workflows which
use activation) all simply returned ``None`` in place of the activated
account. This meant it was not possible to determine, from inspecting
the result, what exactly caused the failure.

In django-registration 3.x, activation failures raise an exception --
:class:`~django_registration.exceptions.ActivationError` -- with a
message and code (such as ``"expired"``), to indicate the cause of
failure. This exception is caught by
:class:`~django_registration.views.ActivationView` and turned into the
template context variable ``activation_error``.


Other changes
~~~~~~~~~~~~~

The URLconf ``registration.urls`` has been removed; it was an alias
for the URLconf of the model-based workflow, which has also been
removed.

The compatibility alias ``registration.backends.default``, which also
pointed to the model-based workflow, has been removed.


Changes during the 2.x release series
-------------------------------------

One major change occurred between django-registration 2.0 and 2.1: the
addition in version 2.1 of the
:class:`~django_registration.validators.ReservedNameValidator`, which is now
used by default on :class:`~django_registration.forms.RegistrationForm` and
its subclasses.

This is technically backwards-incompatible, since a set of usernames
which previously could be registered now cannot be registered, but was
included because the security benefits outweigh the edge cases of the
now-disallowed usernames. If you need to allow users to register with
usernames forbidden by this validator, see its documentation for notes
on how to customize or disable it.

In 2.2, the behavior of the ``RegistrationProfile.expired()`` method
was clarified to accommodate user expectations; it does *not* return
(and thus, ``RegistrationProfile.delete_expired_users()`` does not
delete) profiles of users who had successfully activated.

In django-registration 2.3, the new validators
:func:`~django_registration.validators.validate_confusables` and
:func:`~django_registration.validators.validate_confusables_email` were
added, and are applied by default to the username field and email
field, respectively, of registration forms. This may cause some
usernames which previously were accepted to no longer be accepted, but
like the reserved-name validator this change was made because its
security benefits significantly outweigh the edge cases in which it
might disallow an otherwise-acceptable username or email address. If
for some reason you need to allow registration with usernames or email
addresses containing potentially dangerous use of Unicode, you can
subclass the registration form and remove these validators, though
doing so is not recommended.


Versions prior to 2.0
~~~~~~~~~~~~~~~~~~~~~

A 1.0 release of django-registration existed, but the 2.x series was
compatible with it.

Prior to 1.0, the most widely-adopted version of django-registration
was 0.8; the changes from 0.8 to 2.x were large and significant, and
if any installations on 0.8 still exist and wish to upgrade to more
recent versions, it is likely the most effective route will be to
discard all code using 0.8 and start over from scratch with a 3.x
release.
