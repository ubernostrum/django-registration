.. _custom-user:

Custom user models
==================

When django-registration was first developed, Django's authentication
system supported only its own built-in user model,
:class:`django.contrib.auth.models.User`. More recent versions of
Django have introduced support for `custom user models
<https://docs.djangoproject.com/en/stable/topics/auth/customizing/#substituting-a-custom-user-model>`_.

Older versions of django-registration did not generally support custom
user models due to the additional complexity required. However,
django-registration now can support custom user models. Depending on
how significantly your custom user model differs from Django's
default, you may need to change only a few lines of code; custom user
models significantly different from the default model may require more
work to support.


Overview
--------

The primary issue when using django-registration with a custom user
model will be
:class:`~django_registration.forms.RegistrationForm`. :class:`~django_registration.forms.RegistrationForm`
is a subclass of Django's built-in
:class:`~django.contrib.auth.forms.UserCreationForm`. The only changes
made by django-registration are:

* Apply the reserved name validator
  (:class:`django_registration.validators.ReservedNameValidator`), and

* Make the email field required. By default, Django's user model makes
  this field optional; it is required in
  :class:`~django_registration.forms.RegistrationForm` because
  :ref:`the two-step activation workflow <activation-workflow>`
  requires an email address in order to send account-activation
  instructions to the user.

.. important:: **Custom user models always require a custom form**

   The base :class:`~django_registration.forms.RegistrationForm` class
   inherits the model attribute of Django's
   :class:`~django.contribb.auth.forms.UserCreationForm`. This means
   it will crash, immediately and loudly, with an exception if you try
   to use it when you've told Django to use a custom user model.

   This is not a bug in django-registration. This is a deliberate
   design choice: custom user models offer a huge amount of freedom,
   but that level of freedom also means it's impossible to write a
   single generic form class that will work with any custom user
   model. So django-registration places the responsibility for
   checking compatibility on *you*, the developer.

   The sections below explain how to ensure compatibility with a
   custom user model, and how you can set up the registration views to
   use a form class bound to your custom user model. Again, you
   **must** follow these steps when you have a custom user model, and
   the fact that django-registration crashes with an error message
   when you don't is intentional and not a bug.

In the case where your user model is compatible with the default
behavior of django-registration, (see below) you will be able to
subclass :class:`~django_registration.forms.RegistrationForm`, set it
to use your custom user model as the model, and then configure the
views in django-registration to use your form subclass. For example,
you might do the following (in a `forms.py` module somewhere in your
codebase -- do **not** directly edit django-registration's code):

.. code-block:: python

    from django_registration.forms import RegistrationForm

    from mycustomuserapp.models import MyCustomUser

    
    class MyCustomUserForm(RegistrationForm):
        class Meta(RegistrationForm.Meta):
            model = MyCustomUser

You will also need to specify the fields to include in the form, via
the `fields` declaration.

And then in your URL configuration (example here uses the two-step
activation workflow):

.. code-block:: python

    from django.urls import include, path

    from django_registration.backends.activation.views import RegistrationView
    
    from mycustomuserapp.forms import MyCustomUserForm


    urlpatterns = [
        # ... other URL patterns here
        path('accounts/register/',
            RegistrationView.as_view(
                form_class=MyCustomUserForm
            ),
            name='django_registration_register',
        ),
        path('accounts/',
	    include('django_registration.backends.activation.urls')
	),
	# ... more URL patterns
    ]
    
If your custom user model is not compatible with the built-in
workflows of django-registration (see next section), you will
probably need to subclass the provided views (either the base
registration views, or the views of the workflow you want to use) and
make the appropriate changes for your user model.


Determining compatibility of a custom user model
------------------------------------------------

The built-in workflows and other code of django-registration do as
much as is possible to ensure compatibility with custom user models:
Django provides numerous facilities for retrieving and introspecting
the user model without hard-coding a particular model class or field
names, and django-registration makes use of them.

However, there are still some specific requirements you'll want to be
aware of.


The two-step activation workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :ref:`two-step activation <activation-workflow>` requires that the
following be true of your user model:

* It must set the attribute
  :attr:`~django.contrib.auth.CustomUser.USERNAME_FIELD` to denote the
  field used as the username, and must define the method
  :meth:`~django.contrib.auth.models.AbstractBaseUser.get_username`
  for retrieving the username value. Subclasses of Django's
  :class:`~django.contrib.auth.models.AbstractBaseUser` receive this
  attribute and method automatically.

* It must have a field for storing an email address, and it must
  define the method
  :meth:`~django.contrib.auth.models.AbstractBaseUser.get_email_field_name`,
  which will return the name of the email field. Subclasses of
  Django's :class:`~django.contrib.auth.models.AbstractBaseUser`
  receive this method automatically (and the backing attribute
  :attr:`~django.contrib.auth.models.CustomUser.EmailField` which
  normally stores the name of the email field). This field must be a
  textual field type (:class:`~django.db.models.EmailField`,
  :class:`~django.db.models.CharField` or
  :class:`~django.db.models.TextField`). Note that this field will be
  required by :class:`~django_registration.forms.RegistrationForm`,
  which is a difference from Django's default
  :class:`~django.contrib.auth.forms.UserCreationForm`.

* The username and email fields must be distinct. If you wish to use
  the email address as the username field, you will need to supply
  your own completely custom registration form.

* It must have a field named
  :attr:`~django.contrib.auth.models.User.is_active`, and it must be a
  :class:`~django.db.models.BooleanField` indicating whether the
  user's account is active.

If your custom user model defines additional fields beyond the minimum
requirements, you'll either need to ensure that all of those fields
are optional (i.e., can be `NULL` in your database, or provide a
suitable default value defined in the model), or you'll need to
specify the full list of fields to display in the `fields` section
of the `Meta` declaration of your
:class:`~django_registration.forms.RegistrationForm` subclass.


The one-step workflow
~~~~~~~~~~~~~~~~~~~~~

:ref:`The one-step workflow <one-step-workflow>` places the following
requirements on your user model:

* It must set the attribute
  :attr:`~django.contrib.auth.CustomUser.USERNAME_FIELD` to denote the
  field used as the username, and must define the method
  :meth:`~django.contrib.auth.models.AbstractBaseUser.get_username`
  for retrieving the username value. Subclasses of Django's
  :class:`~django.contrib.auth.models.AbstractBaseUser` receive this
  attribute and method automatically.

* It must define a field named `password` for storing the user's
  password (it will expect to find the value in the field
  `password1` of the registration form).

Also note that :class:`~django_registration.forms.RegistrationForm`
requires the `email` field, so either provide that field on your
model or subclass :class:`~django_registration.forms.RegistrationForm`
and override to remove the `email` field or make it optional.

If your custom user model defines additional fields beyond the minimum
requirements, you'll either need to ensure that all of those fields
are optional (i.e., can be `NULL` in your database, or provide a
suitable default value defined in the model), or you'll need to
specify the full list of fields to display in the `fields` section
of the `Meta` declaration of your
:class:`~django_registration.forms.RegistrationForm` subclass.

Because the one-step workflow logs in the new account immediately
after creating it, you must either use Django's
:class:`~django.contrib.auth.backends.ModelBackend` as an
authentication backend, or use an authentication backend which accepts
a combination of `USERNAME_FIELD` and `password` as sufficient
credentials.
