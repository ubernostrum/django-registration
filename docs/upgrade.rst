.. _upgrade:


Upgrading from previous versions
================================

The current release series of django-registration is the 3.x series, which is
not backwards-compatible with the django-registration 2.x release series.


Changes within the 3.x series
-----------------------------

Within the 3.x release series, there have been several minor changes and
improvements, documented here along with the version in which they occurred.

django-registration 3.4
~~~~~~~~~~~~~~~~~~~~~~~

* The :ref:`reserved names list <reserved-names>` has a new entry: ``"xrpc"``,
  which is used in domain-ownership verification by Bluesky/AT protocol.

* Validation of the email field in registration forms no longer applies
  Django's default email validator, instead applying only django-registration's
  :class:`~django_registration.validators.HTML5EmailValidator` and
  :func:`~django_registration.validators.validate_confusables_email`. Since
  django-registration's validators are significantly stricter, this does not
  actually change the set of email addresses which will be accepted; all it
  does is prevent a duplicate error message displaying when both the default
  Django validator and the django-registration validators reject the email
  address. See `GitHub issue #238
  <https://github.com/ubernostrum/django-registration/issues/238>`_.

* The supported Python and Django versions are changed to: Django 3.2, 4.1, and
  4.2, on Python 3.7 (Django 3.2 only), 3.8, 3.9, 3.10, and 3.11 (Django 4.1
  and 4.2 only).

django-registration 3.3
~~~~~~~~~~~~~~~~~~~~~~~

This release contains no new features or bugfixes. The supported Python and
Django versions are changed to:

* Django 3.2 and 4.0, on Python 3.7 (Django 3.2 only), 3.8, 3.9, and 3.10.

django-registration 3.2
~~~~~~~~~~~~~~~~~~~~~~~

This release contains no new features or bugfixes. The supported Python and
Django versions are changed to:

* Django 2.2, 3.1, and 3.2, on Python 3.6, 3.7, 3.8, and 3.9.

Python 3.5 reached the end of its upstream support cycle in September 2020, and
is no longer supported. Django 3.0 reached the end of its upstream support
cycle in May 2021, and is no longer supported.

django-registration 3.1.2
~~~~~~~~~~~~~~~~~~~~~~~~~

This release fixes a security issue with low severity.

Prior to 3.1.2, django-registration did not apply Django's
:func:`~django.views.decorators.debug.sensitive_post_parameters` decorator to
the base :class:`~django_registration.views.RegistrationView`. This meant that
if detailed error reports, such as `Django's error reports emailed to site
staff
<https://docs.djangoproject.com/en/3.1/howto/error-reporting/#email-reports>`_,
were enabled, and a server-side error occurred during account registration, the
generated error report would include all fields submitted in the HTTP request,
some of which are potentially sensitive depending on the user-account model and
registration workflow in use.

This issue is CVE-2021-21416 and GitHub security advisory GHSA-58c7-px5v-82hh.

Thanks to Martin Morgenstern for reporting this issue.

Django-registration 3.1
~~~~~~~~~~~~~~~~~~~~~~~

* When an attempt was made to use django-registration with a custom user model,
  but *without* explicitly subclassing
  :class:`~django_registration.forms.RegistrationForm` to point to that user
  model, previously the result would be a cryptic exception and error message
  raised from within Django, complaining about trying to work with the
  swapped-out user model. :class:`~django_registration.views.RegistrationView`
  now explicitly raises :exc:`~django.core.exceptions.ImproperlyConfigured`
  with an informative error message to make it clear what has happened, and
  directs the developer to the documentation for using custom user models in
  django-registration.

* A new validator,
  :class:`~django_registration.validators.HTML5EmailValidator`, is included and
  is applied by default to the email field of
  :class:`~django_registration.forms.RegistrationForm`. The HTML5 email address
  grammar is more restrictive than the RFC grammar, but primarily in
  disallowing rare and problematic features.

* Support for Python 2 was dropped, as Python 2 is EOL as of 2020-01-01. As a
  result, support for Django 1.11 (EOL April 2020) was also dropped; the
  minimum supported Django version is now 2.2.


django-registration 3.0.1
~~~~~~~~~~~~~~~~~~~~~~~~~

* The :ref:`custom validators <validators>` are now serializable.

* Although no code changes were required, this release officially marks itself
  compatible with Python 3.7 and with django 2.2.


Changes between django-registration 2.x and 3.x
-----------------------------------------------

Module renaming
~~~~~~~~~~~~~~~

Prior to 3.x, django-registration installed a Python module named
``registration``. To avoid silent incompatibilities, and to conform to more
recent best practices, django-registration 3.x now installs a module named
``django_registration``. Attempts to import from the ``registration`` module will
immediately fail with :exc:`ImportError`.

Many installations will be able to adapt by replacing references to
``registration`` with references to ``django_registration``.


Removal of model-based workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The two-step model-based signup workflow, which has been present since the
first public release of django-registration in 2007, has now been removed. In
its place, it is recommended that you use :ref:`the two-step activation
workflow <activation-workflow>` instead, as that workflow requires no
server-side storage of additional data beyond the user account itself.


Renaming of two-step activation workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`The two-step activation workflow <activation-workflow>` was previously
found at ``registration.backends.hmac``; it has been renamed and is now found at
``registration.backends.activation``.


Renaming of one-step workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`The one-step workflow <one-step-workflow>` was previously found at
``registration.backends.simple``; it has been renamed and is now found at
``registration.backends.one_step``.


Removal of auth URLs
~~~~~~~~~~~~~~~~~~~~

Prior to 3.x, django-registration's default URLconf modules for its built-in
workflows would attempt to include the Django auth views (login, logout,
password reset, etc.) for you. This became untenable with the rewrite of
Django's auth views to be class-based, as it required detecting the set of auth
views and choosing a set of URL patterns at runtime.

As a result, auth views are no longer automatically configured for you; if you
want them, :func:`~django.urls.include` the URLconf ``django.contrib.auth.urls``
at a location of your choosing.


Distinguishing activation failure conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prior to 3.x, failures to activate a user account (in workflows which use
activation) all simply returned :data:`None` in place of the activated
account. This meant it was not possible to determine, from inspecting the
result, what exactly caused the failure.

In django-registration 3.x, activation failures raise an exception --
:exc:`~django_registration.exceptions.ActivationError` -- with a message and
code (such as ``"expired"``), to indicate the cause of failure. This exception is
caught by :class:`~django_registration.views.ActivationView` and turned into
the template context variable ``activation_error``.


Changes to custom user support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Support for custom user models has been brought more in line with the features
Django offers. This affects compatibility of custom user models with
django-registration's default forms and views. In particular, custom user
models should now provide, in addition to
:attr:`~django.contrib.auth.CustomUser.USERNAME_FIELD`, the
:meth:`~django.contrib.auth.models.AbstractBaseUser.get_username` and
:meth:`~django.contrib.auth.models.AbstractBaseUser.get_email_field_name`
methods. See :ref:`the custom user documentation <custom-user>` for details.


Changes to ``success_url``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Both the registration and activation views mimic Django's own generic views in
supporting a choice of ways to specify where to redirect after a successful
registration or activation; you can either set the attribute
:attr:`~django_registration.views.RegistrationView.success_url` on the view
class, or implement the method
:meth:`~django_registration.views.RegistrationView.get_success_url` . However,
there is a key difference between the base Django generic-view version of this,
and the version in django-registration: when calling a
:meth:`~django_registration.views.RegistrationView.get_success_url` method,
django-registration passes the user account as an argument.

This is incompatible with the behavior of Django's base
:class:`~django.views.generic.edit.FormMixin`, which expects
:meth:`~django.views.generic.edit.FormMixin.get_success_url` to take zero
arguments.

Also, earlier versions of django-registration allowed
:attr:`~django_registration.views.RegistrationView.success_url` and
:meth:`~django_registration.views.RegistrationView.get_success_url` to provide
either a string URL, or a tuple of ``(viewname, args, kwargs)`` to pass to
Django's :func:`~django.urls.reverse` helper, in order to work around issues
caused by calling :func:`~django.urls.reverse` at the level of a class
attribute.

In django-registration 3.x, the ``user`` argument to
:meth:`~django_registration.views.RegistrationView.get_success_url` is now
optional, meaning :class:`~django.views.generic.edit.FormMixin`'s default
behavior is now compatible with any
:meth:`~django_registration.views.RegistrationView.get_success_url`
implementation that doesn't require the user object; as a result,
implementations which don't rely on the user object should either switch to
specifying :attr:`~django_registration.views.RegistrationView.success_url` as
an attribute, or change their own signature to ``get_success_url(self,
user=None)``.

Also, the ability to supply the 3-tuple of arguments for
:func:`~django.urls.reverse` has been removed; both
:attr:`~django_registration.views.RegistrationView.success_url` and
:meth:`~django_registration.views.RegistrationView.get_success_url` now *must*
be/return either a string, or a lazy object that resolves to a string. To avoid
class-level calls to :func:`~django.urls.reverse`, use
``django.urls.reverse_lazy()`` instead.


Removed "no free email" form
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Earlier versions of django-registration included a form class,
``RegistrationFormNoFreeEmail``, which attempted to forbid user signups using
common free/throwaway email providers. Since this is a pointless task (the
number of possible domains of such providers is ever-growing), this form class
has been removed.


Template names
~~~~~~~~~~~~~~

Since django-registration's Python module has been renamed from ``registration``
to ``django_registration``, its default template folder has also been renamed,
from ``registration`` to ``django_registration``. Additionally, the following
templates have undergone name changes:

* The default template name for the body of the activation email in the
  two-step activation workflow is now
  ``django_registration/activation_email_body.txt`` (previously, it was
  ``registration/activation_email.txt``)

* The default template name for
  :class:`~django_registration.views.ActivationView` and its subclasses is now
  ``django_registration/activation_failed.html`` (previously, it was
  ``registration/activate.html``).


Renaming of URL patterns
~~~~~~~~~~~~~~~~~~~~~~~~

Prior to 3.x, django-registration's included URLconf modules provided URL
pattern names beginning with ``"registration"``. For example:
``"registration_register"``. In 3.x, these are all renamed to begin with
``"django_registration"``. For example: ``"django_registration_register"``.

Removal of ``cleanupregistration`` management command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The "cleanupregistration" management command, and the
RegistrationProfile.objects.delete_expired_users() and
RegistrationProfile.objects.expired() methods, were removed in
django-registration 3.0.  Deployments which need a way to identify and delete
expired accounts should determine how they wish to do so and implement their
own methods for this.

Other changes
~~~~~~~~~~~~~

The URLconf ``registration.urls`` has been removed; it was an alias for the
URLconf of the model-based workflow, which has also been removed.

The compatibility alias ``registration.backends.default``, which also pointed to
the model-based workflow, has been removed.


Changes during the 2.x release series
-------------------------------------

One major change occurred between django-registration 2.0 and 2.1: the addition
in version 2.1 of the
:class:`~django_registration.validators.ReservedNameValidator`, which is now
used by default on :class:`~django_registration.forms.RegistrationForm` and its
subclasses.

This is technically backwards-incompatible, since a set of usernames which
previously could be registered now cannot be registered, but was included
because the security benefits outweigh the edge cases of the now-disallowed
usernames. If you need to allow users to register with usernames forbidden by
this validator, see its documentation for notes on how to customize or disable
it.

In 2.2, the behavior of the ``RegistrationProfile.expired()`` method was
clarified to accommodate user expectations; it does *not* return (and thus,
``RegistrationProfile.delete_expired_users()`` does not delete) profiles of users
who had successfully activated.

In django-registration 2.3, the new validators
:func:`~django_registration.validators.validate_confusables` and
:func:`~django_registration.validators.validate_confusables_email` were added,
and are applied by default to the username field and email field, respectively,
of registration forms. This may cause some usernames which previously were
accepted to no longer be accepted, but like the reserved-name validator this
change was made because its security benefits significantly outweigh the edge
cases in which it might disallow an otherwise-acceptable username or email
address. If for some reason you need to allow registration with usernames or
email addresses containing potentially dangerous use of Unicode, you can
subclass the registration form and remove these validators, though doing so is
not recommended.


Versions prior to 2.0
---------------------

A 1.0 release of django-registration existed, but the 2.x series was compatible
with it.

Prior to 1.0, the most widely-adopted version of django-registration was 0.8;
the changes from 0.8 to 2.x were large and significant, and if any
installations on 0.8 still exist and wish to upgrade to more recent versions,
it is likely the most effective route will be to discard all code using 0.8 and
start over from scratch with a 3.x release.
