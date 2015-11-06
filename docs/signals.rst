.. _signals:
.. module:: registration.signals


Signals used by django-registration
===================================

Much of ``django-registration``'s customizability comes through the
ability to write and use different workflows for user
registration. However, there are many cases where only a small bit of
additional logic needs to be injected into the registration process,
and writing a custom workflow to support this represents an
unnecessary amount of work. A more lightweight customization option is
provided through two custom signals which the built-in registration
workflows send, and custom workflows are encouraged to send, at
specific points during the registration process; functions listening
for these signals can then add whatever logic is needed.

For general documentation on signals and the Django dispatcher,
consult `Django's signals documentation
<http://docs.djangoproject.com/en/stable/topics/signals/>`_. This
documentation assumes that you are familiar with how signals work and
the process of writing and connecting functions which will listen for
signals.


.. data:: user_activated

   Sent when a user account is activated (not applicable to all
   workflows). Provides the following arguments:

   ``sender``
       The :class:`~registration.views.ActivationView` subclass used
       to activate the user.

   ``user``
        A user-model instance representing the activated account.

   ``request``
       The ``HttpRequest`` in which the account was activated.


.. data:: user_registered

   Sent when a new user account is registered. Provides the following
   arguments:

   ``sender``
       The :class:`~registration.views.RegistrationView` subclass used
       to register the account.

   ``user``
        A user-model instance representing the new account.

   ``request``
        The ``HttpRequest`` in which the new account was registered.
