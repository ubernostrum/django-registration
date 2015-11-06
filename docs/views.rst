.. _views:
.. module:: registration.views

Base view classes
=================

In order to allow the utmost flexibility in customizing and supporting
different workflows, ``django-registration`` makes use of Django's
support for `class-based views
<https://docs.djangoproject.com/en/stable/topics/class-based-views/>`_. Included
in ``django-registration`` are two base classes which can be
subclassed to implement whatever workflow is required.

The built-in workflows in ``django-registration`` provide their own
subclasses of these views, and the documentation for those workflows
will indicate customization points specific to those subclasses. The
following reference covers useful attributes and methods of the base
classes, for use in writing your own custom subclasses.

.. class:: RegistrationView

   A subclass of Django's `FormView
   <https://docs.djangoproject.com/en/stable/ref/class-based-views/generic-editing/#formview>`_,
   which provides the infrastructure for supporting user registration.

   Since it's a subclass of ``FormView``, ``RegistrationView`` has all
   the usual attributes and methods you can override.

   When writing your own subclass, one method is required:

   .. method:: register(form)

      Implement your registration logic here. ``form`` will be the
      (already-validated) form filled out by the user during the
      registration process (i.e., a valid instance of
      :class:`registration.forms.RegistrationForm` or a subclass of
      it).

      This method should return the newly-registered user instance,
      and should send the signal
      :data:`registration.signals.user_registered`.

   Useful optional places to override or customize on a
   ``RegistrationView`` subclass are:

   .. attribute:: disallowed_url

      The URL to redirect to when registration is disallowed. Should
      be a `string name of a URL pattern
      <https://docs.djangoproject.com/en/stable/topics/http/urls/#naming-url-patterns>`_.
      Default value is ``"registration_disallowed"``.

   .. attribute:: form_class

      The form class to use for user registration. Can be overridden
      on a per-request basis (see below). Should be the actual class
      object; by default, this class is
      :class:`registration.forms.RegistrationForm`.

   .. attribute:: success_url

      The URL to redirect to after successful registration.  A string
      containing a (relative) URL, or a string name of a URL pattern,
      or a 3-tuple of arguments suitable for passing to Django's
      `redirect shortcut
      <https://docs.djangoproject.com/en/stable/topics/http/shortcuts/#redirect>`_. Can
      be overridden on a per-request basis (see below). Default value
      is ``None``, so that per-request customization is used instead.

   .. attribute:: template_name

      The template to use for user registration. Should be a
      string. Default value is
      ``registration/registration_form.html``.

   .. method:: get_form_class()

      Select a form class to use on a per-request basis. If not
      overridden, will use :attr:`~form_class`. Should be the actual
      class object.

   .. method:: get_success_url(user)

      Return a URL to redirect to after successful registration, on a
      per-request or per-user basis. If not overridden, will use
      :attr:`~success_url`. Should return a string containing a
      (relative) URL, or a string name of a URL pattern, or a 3-tuple
      of arguments suitable for passing to Django's ``redirect``
      shortcut.

   .. method:: registration_allowed()

      Should return a boolean indicating whether user registration is
      allowed, either in general or for this specific request.


.. class:: ActivationView

   A subclass of Django's `TemplateView
   <https://docs.djangoproject.com/en/stable/ref/class-based-views/base/#templateview>`_
   which provides support for a separate account-activation step, in
   workflows which require that.

   One method is required:

   .. method:: activate(*args, **kwargs)

      Implement your activation logic here. You are free to configure
      your URL patterns to pass any set of positional or keyword
      arguments to ``ActivationView``, and they will in turn be passed
      to this method.

      This method should return the newly-activated user instance (if
      activation was successful), or boolean ``False`` if activation
      was not successful.

   Useful places to override or customize on an ``ActivationView``
   subclass are:

   .. attribute:: template_name

      The template to use for user activation. Should be a
      string. Default value is ``registration/activate.html``.

   .. method:: get_success_url(user)

      Return a URL to redirect to after successful registration, on a
      per-request or per-user basis. If not overridden, will use
      :attr:`~success_url`. Should return a string containing a
      (relative) URL, or a string name of a URL pattern, or a 3-tuple
      of arguments suitable for passing to Django's ``redirect``
      shortcut.
