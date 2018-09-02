.. _faq:

Frequently-asked questions
==========================

The following are miscellaneous common questions and answers related
to installing/using django-registration, culled from bug reports,
emails and other sources.


General
-------

How can I support social-media and other auth schemes, like Facebook or GitHub?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By using `django-allauth
<https://pypi.python.org/pypi/django-allauth>`_. No single application
can or should provide a universal API for every authentication system
ever developed; django-registration sticks to making it easy to
implement typical signup workflows using Django's own user model and
auth system (with some ability to use custom user models), while apps
like ``django-allauth`` handle integration with third-party
authentication services far more effectively.

What license is django-registration under?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

django-registration is offered under a three-clause BSD-style license;
this is `an OSI-approved open-source license
<http://www.opensource.org/licenses/bsd-license.php>`_, and allows you
a large degree of freedom in modifying and redistributing the
code. For the full terms, see the file ``LICENSE`` which came with
your copy of django-registration; if you did not receive a copy of
this file, you can view it online at
<https://github.com/ubernostrum/django-registration/blob/master/LICENSE>.

What versions of Django and Python are supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As of django-registration |release|, Django 1.11, 2.0 and 2.1 are
supported, on Python 2.7, (Django 1.11 only), 3.4 (Django 1.11 and 2.0
only), 3.5, 3.6 and 3.7 (Django 2.0 and 2.1 only).

I found a bug or want to make an improvement!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. important:: **Reporting security issues**

   If you believe you have found a security issue in
   django-registration, please do *not* use the public GitHub issue
   tracker to report it. Instead, you can `contact the author
   privately <https://www.b-list.org/contact/>`_ to report the issue.

The canonical development repository for django-registration is online
at <https://github.com/ubernostrum/django-registration>. Issues and
pull requests can both be filed there.

If you'd like to contribute to django-registration, that's great! Just
please remember that pull requests should include tests and
documentation for any changes made, and that following `PEP 8
<https://www.python.org/dev/peps/pep-0008/>`_ is mandatory. Pull
requests without documentation won't be merged, and PEP 8 style
violations or test coverage below 100% are both configured to break
the build.

How secure is django-registration?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Over the decade-plus history of django-registration, there have been
no security issues reported which required new releases to
remedy. This doesn't mean, though, that django-registration is
perfectly secure: much will depend on ensuring best practices in
deployment and server configuration, and there could always be
security issues that just haven't been recognized yet.

django-registration does, however, try to avoid common security
issues:

* django-registration |release| only supports versions of Django which
  were receiving upstream security support at the time of release.

* django-registration does not attempt to generate or store passwords,
  and does not transmit credentials which could be used to log in (the
  only "credential" ever sent out by django-registration is an
  activation key used in the two-step activation workflow, and that
  key can only be used to make an account active; it cannot be used to
  log in).

* django-registration works with Django's own security features
  (including cryptographic features) where possible, rather than
  reinventing its own.

For more details, see :ref:`the security guide <security>`.

How do I run the tests?
~~~~~~~~~~~~~~~~~~~~~~~

django-registration's tests are run using `tox
<https://tox.readthedocs.io/>`_, but typical installation of
django-registration (via ``pip install django-registration``) will not
install the tests.

To run the tests, download the source (``.tar.gz``) distribution of
django-registration |release| from `its page on the Python Package
Index <https://pypi.org/project/django-registration/>`_, unpack it
(``tar zxvf django-registration-|release|.tar.gz`` on most Unix-like
operating systems), and in the unpacked directory run ``tox``.

Note that you will need to have ``tox`` installed already (``pip
install tox``), and to run the full test matrix you will need to have
each supported version of Python available. To run only the tests for
a specific Python version and Django version, you can invoke ``tox``
with the ``-e`` flag. For example, to run tests for Python 3.6 and
Django 2.0: ``tox -e py36-django20``.

   
Installation and setup
----------------------

How do I install django-registration?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Full instructions are available in :ref:`the installation guide
<install>`. For configuration, see :ref:`the quick start guide
<quickstart>`.

Does django-registration come with any sample templates I can use right away?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No, for two reasons:

1. Providing default templates with an application is ranges from hard
   to impossible, because different sites can have such wildly
   different design and template structure. Any attempt to provide
   templates which would work with all the possibilities would
   probably end up working with none of them.

2. A number of things in django-registration depend on the specific
   registration workflow you use, including the variables which end up
   in template contexts. Since django-registration has no way of
   knowing in advance what workflow you're going to be using, it also
   has no way of knowing what your templates will need to look like.

Fortunately, however, django-registration has good documentation which
explains what context variables will be available to templates, and so
it should be easy for anyone who knows Django's template system to
create templates which integrate with their own site.


Configuration
-------------

Do I need to rewrite the views to change the way they behave?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not always. Any behavior controlled by an attribute on a class-based
view can be changed by passing a different value for that attribute in
the URLconf. See `Django's class-based view documentation
<https://docs.djangoproject.com/en/stable/topics/class-based-views/#simple-usage-in-your-urlconf>`_
for examples of this.

For more complex or fine-grained control, you will likely want to
subclass :class:`~django_registration.views.RegistrationView` or
:class:`~django_registration.views.ActivationView`, or both, add your
custom logic to your subclasses, and then create a URLconf which makes
use of your subclasses.
    
I don't want to write my own URLconf because I don't want to write patterns for all the auth views!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You're in luck, then; Django provides a URLconf for this, at
``django.contrib.auth.urls``.

I don't like the names you've given to the URL patterns!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In that case, you should feel free to set up your own URLconf which
uses the names you want.

I'm using a custom user model; how do I make that work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See :ref:`the custom user documentation <custom-user>`.


Tips and tricks
---------------

How do I close user signups?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you haven't modified the behavior of the
:meth:`~django_registration.views.RegistrationView.registration_allowed`
method in :class:`~django_registration.views.RegistrationView`, you can
use the setting :data:`~django.conf.settings.REGISTRATION_OPEN` to
control this; when the setting is ``True``, or isn't supplied,
user registration will be permitted. When the setting is
``False``, user registration will not be permitted.

How do I log a user in immediately after registration or activation?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Take a look at the implementation of :ref:`the one-step workflow
<one-step-workflow>`, which logs a user in immediately after
registration.

How do I manually activate a user?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In :ref:`the two-step activation workflow <activation-workflow>`,
toggle the ``is_active`` field of the user in the admin.

How do I delete expired unactivated accounts?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Perform a query for those accounts, and call the ``delete()`` method
of the resulting ``QuerySet``. Since django-registration doesn't know
in advance what your definition of "expired" will be, it leaves this
step to you.

How do I allow Unicode in usernames?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use Python 3. Django's username validation allows any word character
plus some additional characters, but the definition of "word
character" depends on the Python version in use. On Python 2, only
ASCII will be permitted; on Python 3, usernames containing word
characters matched by a regex with the ``UNICODE`` flag will be
accepted.

How do I tell why an account's activation failed?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're using :ref:`the two-step activation workflow
<activation-workflow>`, the template context will contain a variable
``activation_error`` containing the information passed when the
:exc:`django_registration.exceptions.ActivationError` was raised. This
will indicate what caused the failure.