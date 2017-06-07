.. _deprecations:


Feature and API deprecation cycle
=================================

The following features or APIs of django-registration are deprecated
and scheduled to be removed in future releases. Please make a note of
this and update your use of django-registration accordingly. When
possible, deprecated features will emit a ``DeprecationWarning`` as an
additional warning of pending removal.


``registration.urls``
---------------------

**Will be removed in:** django-registration 3.0

This URLconf was provided in the earliest days of django-registration,
when :ref:`the model-based workflow <model-workflow>` was the only one
provided. Sites using the model-based workflow should instead
``include()`` the URLconf
``registration.backends.model_activation.urls``.


``registration.backends.default``
---------------------------------

**Will be removed in:** django-registration 3.0

Once django-registration began supporting multiple workflows, the
model-based workflow was moved to
``registration.backends.default``. Later, it was renamed to
``registration.backends.model_activation``, but a module was left in
place at ``registration.backends.default`` for compatibility.

Sites using the model-based workflow should ensure all imports are
from ``registration.backends.model_activation``.


``registration.auth_urls``
--------------------------

**Will be removed in:** django-registration 3.0

For convenience, each URLconf provided in django-registration also
sets up URLs for the views in ``django.contrib.auth`` (login, logout,
password change, and password reset). These URLs are identical --
except for the names assigned to them -- to those defined in
``django.contrib.auth.urls``.

As of 3.0, ``registration.auth_urls`` will be removed, and
django-registration will encourage users to instead ``include()`` the
URLconf ``django.contrib.auth.urls`` at an appropriate location in
their root URLconf.


Expired-account cleanup
-----------------------

**Will be removed in:** django-registration 3.0

The model-based workflow includes several pieces of code for deleting
"expired" -- registered but never activated -- accounts. This was
originally intended as a convenience, but several contentious bug
reports have shown that it is less convenient and more prone to
ambiguity than desired. As a result, this code will be removed in
3.0. This entails removing the following:

* The :meth:`~registration.RegistrationManager.expired` method

* The :meth:`~registration.RegistrationManager.delete_expired_users`
  method

* The ``cleanupregistration`` management command, which invokes the
  ``delete_expired_users`` method.

Sites wishing to clean up expired accounts will need to implement a
method for doing this which conforms to their needs and their
interpretation of "expired".