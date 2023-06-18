.. _custom-user:

Custom user models
==================

Django's built-in auth system provides a default model for user accounts, but
also supports replacing that default with `a custom user model
<https://docs.djangoproject.com/en/stable/topics/auth/customizing/#substituting-a-custom-user-model>`_. Many
projects choose to use a custom user model from the start of their development,
even if it begins as a copy of the default model, in order to avoid the
difficulty of migrating to a custom user model later on.

In general, django-registration will work with a custom user model, though at
least some additional configuration is always required in order to do so. If
you are using a custom user model, please read this document thoroughly
*before* using django-registration, in order to ensure you've taken all the
necessary steps to ensure support.

The process for using a custom user model with django-registration can be
summarized as follows:

1. Compare your custom user model to the assumptions made by the built-in
   registration workflows.

2. If your user model is compatible with those assumptions, write a short
   subclass of :class:`~django_registration.forms.RegistrationForm` pointed at
   your user model, and instruct django-registration to use that form.

3. If your user model is *not* compatible with those assumptions, either write
   subclasses of the appropriate views in django-registration which will be
   compatible with your user model, or modify your user model to be compatible
   with the built-in views.

These steps are covered in more detail below.


Compatibility of the built-in workflows with custom user models
---------------------------------------------------------------

Django provides a number of helpers to make it easier for code to generically
work with custom user models, and django-registration makes use of
these. However, the built-in registration workflows must still make *some*
assumptions about the structure of your user model in order to work with it. If
you intend to use one of django-registration's built-in registration workflows,
please carefully read the appropriate section to see what it expects from your
user model.


The two-step activation workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`The two-step activation workflow <activation-workflow>` requires that the
following be true of your user model:

* Your user model must set the attribute
  :attr:`~django.contrib.auth.models.CustomUser.USERNAME_FIELD` to indicate the
  field used as the username.

* Your user model must have a field (of some textual type, ideally
  :class:`~django.db.models.EmailField`) for storing an email address, and it
  must define the method
  :meth:`~django.contrib.auth.models.AbstractBaseUser.get_email_field_name` to
  indicate the name of the email field.

* The username and email fields must be distinct. If you wish to use the email
  address as the username, you will need to write your own completely custom
  registration form.

* Your user model must have a field named
  :attr:`~django.contrib.auth.models.User.is_active`, and that field must be a
  :class:`~django.db.models.BooleanField` indicating whether the user's account
  is active.

If your user model is a subclass of Django's
:class:`~django.contrib.auth.models.AbstractBaseUser`, all of the above will be
automatically handled for you.

If your custom user model defines additional fields beyond the minimum
requirements, you'll either need to ensure that all of those fields are
optional (i.e., can be ``NULL`` in your database, or provide a suitable default
value defined in the model), or specify the correct list of fields to display
in your :class:`~django_registration.forms.RegistrationForm` subclass.


The one-step workflow
~~~~~~~~~~~~~~~~~~~~~

:ref:`The one-step workflow <one-step-workflow>` places the following
requirements on your user model:

* Your user model must set the attribute
  :attr:`~django.contrib.auth.models.CustomUser.USERNAME_FIELD` to indicate the
  field used as the username.

* It must define a textual field named ``password`` for storing the user's
  password.

Also note that the base :class:`~django_registration.forms.RegistrationForm`
includes and requires an email field, so either provide that field on your
model and set the
:meth:`~django.contrib.auth.models.AbstractBaseUser.get_email_field_name`
attribute to indicate which field it is, or subclass
:class:`~django_registration.forms.RegistrationForm` and override to remove the
`email` field or make it optional.

If your user model is a subclass of Django's
:class:`~django.contrib.auth.models.AbstractBaseUser`, all of the above will be
automatically handled for you.

If your custom user model defines additional fields beyond the minimum
requirements, you'll either need to ensure that all of those fields are
optional (i.e., can be ``NULL`` in your database, or provide a suitable default
value defined in the model), or specify the correct list of fields to display
in your :class:`~django_registration.forms.RegistrationForm` subclass.

Because the one-step workflow logs in the new account immediately after
creating it, you also must either use Django's
:class:`~django.contrib.auth.backends.ModelBackend` as an `authentication
backend
<https://docs.djangoproject.com/en/stable/topics/auth/customizing/#other-authentication-sources>`_,
or use an authentication backend which accepts a combination of
``USERNAME_FIELD`` and ``password`` as sufficient credentials to authenticate a
user.


Writing your form subclass
--------------------------

The base :class:`~djangqo_registration.views.RegistrationView` contains
code which compares the declared model of your registration form with
the user model of your Django installation. If these are not the same
model, the view will deliberately crash by raising an
:exc:`~django.core.exceptions.ImproperlyConfigured` exception, with an
error message alerting you to the problem.

This will happen automatically if you attempt to use django-registration with a
custom user model and also attempt to use the default, unmodified
:class:`~django-registration.forms.RegistrationForm`. This is, again, a
deliberate design feature of django-registration, and not a bug:
django-registration has no way of knowing in advance if your user model is
compatible with the assumptions made by the built-in registration workflows
(see above), so it requires you to take the explicit step of replacing the
default registration form as a way of confirming you've manually checked the
compatibility of your user model.

In the case where your user model is compatible with the default behavior of
django-registration, you will be able to subclass
:class:`~django_registration.forms.RegistrationForm`, set it to use your custom
user model as the model, and then configure the views in django-registration to
use your form subclass. For example, you might do the following (in a
``forms.py`` module somewhere in your codebase -- do **not** directly edit
django-registration's code):

.. code-block:: python

    from django_registration.forms import RegistrationForm

    from mycustomuserapp.models import MyCustomUser


    class MyCustomUserForm(RegistrationForm):
        class Meta(RegistrationForm.Meta):
            model = MyCustomUser

You may also need to specify the fields to include in the form, if the set of
fields to include is different from the default set specified by the base
:class:`~django_registration.forms.RegistrationForm`.

Then in your URL configuration (example here uses the two-step activation
workflow), configure the registration view to use the form class you wrote:

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


Incompatible user models
------------------------

If your custom user model is not compatible with the built-in workflows of
django-registration, you have several options.

One is to subclass the built-in form and view classes of django-registration
and make the necessary adjustments to achieve compatibility with your user
model. For example, if you want to use the two-step activation workflow, but
your user model uses a completely different way of marking accounts
active/inactive (compared to the the assumed ``is_active`` field), you might
write subclasses of that workflow's
:class:`~django_registration.backends.activation.views.RegistrationView` and
:class:`~django_registration.backends.activation.views.ActivationView` which
make use of your user model's mechanism for marking accounts active/inactive,
and then use those views along with an appropriate subclass of
:class:`~django_registration.forms.RegistrationForm`.

Or, if the incompatibilities are relatively minor and you don't mind making the
change, you might use Django's migration framework to adjust your custom user
model to match the assumptions made by django-registration's built-in
workflows, thus allowing them to be used unmodified.

Finally, it may sometimes be the case that a given user model requires a
completely custom set of form and view classes to support. Typically, this will
also involve an account-registration process far enough from what
django-registration's built-in workflows provide that you would be writing your
own workflow in any case.
