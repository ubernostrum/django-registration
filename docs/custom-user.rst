.. _custom-user:

Custom user models
==================

When ``django-registration`` was first developed, Django's
authentication system supported only its own built-in user model,
``django.contrib.auth.models.User``. More recent versions of Django
have introduced support for `custom user models
<https://docs.djangoproject.com/en/stable/topics/auth/customizing/#substituting-a-custom-user-model>`_.

Older versions of ``django-registration`` did not generally support
custom user models due to the additional complexity required; as of
version |version|, however, ``django-registration`` now can support
custom user models. Depending on how significantly your custom user
model differs from Django's default, you may need to change only a few
lines of code; custom user models significantly different from the
default model may require more work to support.


Overview
--------

The primary issue when using ``django-registration`` with a custom
user model will be
:class:`~registration.forms.RegistrationForm`. ``RegistrationForm`` is
a subclass of Django's built-in ``UserCreationForm``, which in turn is
a ``ModelForm`` with its model set to
``django.contrib.auth.models.User``. The only changes made by
``django-registration`` are to apply the reserved name validator
(:class:`registration.validators.ReservedNameValidator`) and make the
``email`` field required (by default, Django's user model makes this
field optional; it is required in ``RegistrationForm`` because two of
the three built-in workflows of ``django-registration`` require an
email address in order to send account-activation instructions to the
user). As a result, you will always be required to supply a custom
form class when using ``django-registration`` with a custom user
model.

In the case where your user model is compatible with the default
behavior of ``django-registration``, (see below) you will be able to
simply subclass ``RegistrationForm``, set it to use your custom user
model as the model, and then configure the views in
``django-registration`` to use your form subclass. For example, you
might do the following (in a ``forms.py`` module somewhere in your
codebase -- do **not** directly edit ``django-registration``'s code):

.. code-block:: python

    from registration.forms import RegistrationForm

    from mycustomuserapp.models import MyCustomUser

    
    class MyCustomUserForm(RegistrationForm):
        class Meta:
            model = MyCustomUser

And then in your URL configuration (example here uses the HMAC
activation workflow):

.. code-block:: python

    from django.conf.urls import include, url

    from registration.backends.hmac.views import RegistrationView
    
    from mycustomuserapp.forms import MyCustomUserForm


    urlpatterns = [
        # ... other URL patterns here
        url(r'^accounts/register/$',
            RegistrationView.as_view(
                form_class=MyCustomUserForm
            ),
            name='registration_register',
        ),
        url(r'^accounts/', include('registration.backends.hmac.urls')),
    ]
    
If your custom user model is not compatible with the built-in
workflows of ``django-registration`` (see next section), you will
probably need to subclass the provided views (either the base
registration views, or the views of the workflow you want to use) and
make the appropriate changes for your user model.


Determining compatibility of a custom user model
------------------------------------------------

The built-in workflows and other code of ``django-registration`` do as
much as is possible to ensure compatibility with custom user models;
``django.contrib.auth.models.User`` is never directly imported or
referred to, and all code in ``django-registration`` instead uses
``settings.AUTH_USER_MODEL`` or
``django.contrib.auth.get_user_model()`` to refer to the user model,
and ``USERNAME_FIELD`` when access to the username is required.

However, there are still some specific requirements you'll want to be
aware of.

The two-step activation workflows -- both :ref:`HMAC <hmac-workflow>`-
and :ref:`model <model-workflow>`-based -- require that your user
model have the following fields:

* ``email`` -- a ``CharField`` or ``EmailField`` holding the user's
  email address. Note that this field is required by
  ``RegistrationForm``, which is a difference from Django's default
  ``UserCreationForm``.

* ``is_active`` -- a ``BooleanField`` indicating whether the user's
  account is active.

You also *must* specify the attribute ``USERNAME_FIELD`` on your user
model to denote the field used as the username. Additionally, your
user model must implement the ``email_user`` method for sending email
to the user.

The model-based activation workflow requires one additional field:

* ``date_joined`` -- a ``DateField`` or ``DateTimeField`` indicating
  when the user's account was registered.

:ref:`The simple one-step workflow <simple-workflow>` requires that
your user model set ``USERNAME_FIELD``, and requires that it define a
field named ``password`` for storing the user's password; the
combination of ``USERNAME_FIELD`` and ``password`` must be sufficient
to log a user in. Also note that ``RegistrationForm`` requires the
``email`` field, so either provide that field on your model or
subclass ``RegistrationForm``.

If your custom user model defines additional fields beyond the minimum
requirements, you'll either need to ensure that all of those fields
are optional (i.e., can be ``NULL`` in your database, or provide a
suitable default value defined in the model), or you'll need to
specify the full list of fields to display in the ``fields`` option of
your ``RegistrationForm`` subclass.