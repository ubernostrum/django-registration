.. _custom-user:

Custom user models
==================

Django's built-in auth system provides a default model for user accounts, but
also supports replacing that default with `a custom user model
<https://docs.djangoproject.com/en/stable/topics/auth/customizing/#substituting-a-custom-user-model>`_. Many
projects choose to use a custom user model from the start of their development,
even if it begins as a copy of the default model, in order to avoid the
difficulty of migrating to a custom user model later on.

In general, ``django-registration`` will work with a custom user model, though
there is some required configuration. If you are using a custom user model,
please read this document thoroughly *before* using ``django-registration``, in
order to ensure you've taken all the necessary steps to ensure support.


Required attributes and methods
-------------------------------

The following attributes *must* be present on your user model:

* :attr:`~django.contrib.auth.models.CustomUser.EMAIL_FIELD`: a :class:`str`
  specifying the name of the field containing the user's email address.

* :attr:`~django.contrib.auth.models.CustomUser.USERNAME_FIELD`: a :class:`str`
  specifying the name of the field containing the user's "username". If you use
  the email address as the primary "username"/identifier, set this to the same
  field name as ``EMAIL_FIELD``.

* :attr:`~django.contrib.auth.models.CustomUser.REQUIRED_FIELDS`: a
  :class:`list` of names of fields on your user model which must be included in
  the registration form.

Django's :class:`~django.contrib.auth.models.AbstractUser`, which is what many
custom user models will inherit from and also what the default Django user
model inherits from, sets all three of these, and generally for a custom user
model you would only need to override ``REQUIRED_FIELDS`` in order to specify
any additional custom fields of your model which should be included in the
registration form.

However, if you have a custom user model which inherits from Django's
:class:`~django.contrib.auth.models.AbstractBaseUser` (which is an even more
minimal base class than ``AbstractUser``), or which does not inherit from any
of Django's abstract base user classes, you will need to set all three of the
above attributes on your custom user model for it to be usable with this form.

Additionally, the following two methods may be required on your model:

* If you are using the default
  :class:`~django_registration.forms.RegistrationForm` or a subclass of it,
  your user model must implement the
  :meth:`~django.contrib.auth.models.AbstractBaseUser.set_password` method to
  store the user's selected password. If your user model inherits from
  ``AbstractUser`` or ``AbstractBaseUser``, this is implemented for you.

* If you use a registration workflow which sends an email to the
  newly-registered user (such as :ref:`the built-in two-step activation
  workflow <activation-workflow>`), your user model must implement the
  :meth:`~django.contrib.auth.models.User.email_user` method, with the same API
  as Django's implementation. If your user model inherits from
  ``AbstractUser``, this is implemented for you.


Compatibility of the built-in workflows with custom user models
---------------------------------------------------------------

Django provides a number of helpers to make it easier for code to generically
work with custom user models, and ``django-registration`` makes use of
these. However, the built-in registration workflows must still make *some*
assumptions about the structure of your user model in order to work with it. If
you intend to use one of ``django-registration``'s built-in registration
workflows, please carefully read the appropriate section to see what it expects
from your user model.


The two-step activation workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to the general requirements above, :ref:`The two-step activation
workflow <activation-workflow>` requires that the following be true of your
user model:

* Your user model must have a field named
  :attr:`~django.contrib.auth.models.User.is_active`, and that field must be a
  :class:`~django.db.models.BooleanField` indicating whether the user's account
  is active. If your user model inherits from Django's
  :class:`~django.contrib.auth.models.AbstractUser`, this field is defined for
  you.


The one-step workflow
~~~~~~~~~~~~~~~~~~~~~

Because :ref:`the one-step workflow <one-step-workflow>` logs in the new
account immediately after creating it, you must either use Django's
:class:`~django.contrib.auth.backends.ModelBackend` as an `authentication
backend
<https://docs.djangoproject.com/en/stable/topics/auth/customizing/#other-authentication-sources>`_,
or else use an authentication backend which accepts a combination of your
model's ``USERNAME_FIELD`` and a password value named ``"password"`` as
sufficient credentials to authenticate a user.
