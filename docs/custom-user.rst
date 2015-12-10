.. _custom-user:

Custom user models
==================

When ``django-registration`` was first developed, Django's
authentication system supported only its own built-in user model,
``django.contrib.auth.models.User``. More recent versions of Django
have introduced support for `custom user models
<https://docs.djangoproject.com/en/stable/topics/auth/customizing/#substituting-a-custom-user-model>`_.

It is possible to use ``django-registration`` with a custom user
model, so long as certain factors are accounted for.

.. warning:: **Using email address as username**

   If your custom user model treats the email address as a username,
   or otherwise does not have distinct email address and username
   fields, you **must** write a custom registration workflow including
   custom registration form; the built-in workflows of
   ``django-registration`` will not function with a user model which
   uses the email address as a username.
