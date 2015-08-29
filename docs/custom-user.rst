.. _custom-user:

Custom user models
==================

When ``django-registration`` was first developed, Django's
authentication system supported only its own built-in user model,
``django.contrib.auth.models.User``. More recent versions of Django,
however, have introduced support for `custom user models
<https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#substituting-a-custom-user-model>`_. It
is possible to use ``django-registration`` with a custom user model,
so long as certain factors are accounted for.


Writing a custom registration workflow
--------------------------------------

The most straightforward way to guarantee compatibility with a custom
user model is simply to write your own custom registration workflow,
subclassing :class:`~registration.views.RegistrationView`,
:class:`~registration.views.ActivationView`, and
:class:`~registration.forms.RegistrationForm` as necessary. Refer to
the documentation for those classes for notes on how to customize
them.


Using the built-in workflows
----------------------------

If you want to use one of the registration workflows built in to
``django-registration``, there is some accommodation for custom user
models. :ref:`The two-step model workflow <model-workflow>` uses a
model with a ``OneToOneField`` to the user model, and uses the
recommended practice of referring to it via the
``settings.AUTH_USER_MODEL`` setting. All built-in workflows also
avoid importing or directly referring to Django's default user model,
instead using the ``get_user_model()`` helper provided in
``django.contrib.auth`` to obtain a reference to whatever model has
been specified to represent users.

However, all of these workflows do make some assumptions about the
structure of your user model.

The two-step workflows (both model-based and :ref:`HMAC-based
<hmac-workflow>` require that your user model define the following
fields, which are found on Django's default user model:

* ``username`` -- a ``CharField`` holding the user's username.

* ``email`` -- a ``CharField`` or ``EmailField`` holding the user's
  email address.

* ``password`` -- a ``CharField`` holding the user's password.

* ``is_active`` -- a ``BooleanField`` indicating whether the user's
  account is active.

Additionally, the model-based workflow requires this field:

* ``date_joined`` -- a ``DateField`` or ``DateTimeField`` indicating
  when the user joined the site.

The model-based and HMAC workflows also require that the user model
define a manager class named ``objects``, and that this manager class
provide a method ``create_user``, which will create and return a user
instance from the arguments ``username``, ``email``, and ``password``,
and require that the user model provide the ``email_user`` method on
instances.

The simple one-step workflow requires ``username``, ``email`` and
``password``, and requires the existence of an ``objects`` manager
defining ``create_user``, as in the default workflow.

If your custom user model cannot meet these API requirements, your
only option for using ``django-registration`` will be to write your
own registration workflow.

If you wish to write your own subclasses of the forms and views from
the model-based workflow, but will be customizing them to an
incompatible custom user model, also note that you **must not** add
``registration`` to your ``INSTALLED_APPS`` setting, as doing so would
install the default workflow's
:class:`~registration.models.RegistrationProfile` model, which does
make the above-noted assumptions about the structure of your user
model.