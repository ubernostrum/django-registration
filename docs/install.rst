.. _install:


Installation guide
==================

Before installing django-registration, you'll need to have a copy
of `Django <https://www.djangoproject.com>`_ already installed. For
information on obtaining and installing Django, consult the `Django
download page <https://www.djangoproject.com/download/>`_, which
offers convenient packaged downloads and installation instructions.

The |release| release of django-registration supports Django 1.11, 2.0
and 2.1, on the following Python versions:

* Django 1.11 supports Python 2.7, 3.4, 3.5 and 3.6.

* Django 2.0 supports Python 3.4, 3.5, 3.6 and 3.7.

* Django 2.1 supports Python 3.5, 3.6 and 3.7..


.. important:: **Older Python and Django versions**

   Previous django-registration 2.x releases supported older versions
   of Django and Python. However, django-registration |release|
   supports only those versions of Django and Python which were
   receiving upstream support at the time of release. If you need to
   continue using an older version of Django or Python, you must also
   use an older version of django-registration.
   

Normal installation
-------------------

The preferred method of installing django-registration is via
``pip``, the standard Python package-installation tool. If you don't
have ``pip``, instructions are available for `how to obtain and
install it <https://pip.pypa.io/en/latest/installing.html>`_. If
you're using Python 2.7.9 or later (for Python 2) or Python 3.4 or
later (for Python 3), ``pip`` came bundled with your installation of
Python.

Once you have ``pip``, type::

    pip install django-registration

If you don't have a copy of a compatible version of Django, this will
also automatically install one for you, and will install a third-party
library required by some of django-registration's validation code.


Installing from a source checkout
---------------------------------

If you want to work on django-registration, you can obtain a source
checkout.

The development repository for django-registration is at
<https://github.com/ubernostrum/django-registration>. If you have `git
<http://git-scm.com/>`_ installed, you can obtain a copy of the
repository by typing::

    git clone https://github.com/ubernostrum/django-registration.git

From there, you can use normal git commands to check out the specific
revision you want, and install it using ``pip install -e .`` (the
``-e`` flag specifies an "editable" install, allowing you to change
code as you work on django-registration, and have your changes picked
up automatically).


Next steps
----------

To get up and running quickly, check out :ref:`the quick start guide
<quickstart>`. For full documentation, see :ref:`the documentation
index <index>`.