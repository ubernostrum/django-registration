.. _install:


Installation guide
==================

The |release| release of django-registration supports Django 1.11,
2.0, 2.1, and 2.2 on the following Python versions:

* Django 1.11 supports Python 2.7, 3.4, 3.5 and 3.6.

* Django 2.0 supports Python 3.4, 3.5, 3.6 and 3.7.

* Django 2.1 supports Python 3.5, 3.6 and 3.7.

* Django 2.2 supports Python 3.5, 3.6, and 3.7.


Normal installation
-------------------

The preferred method of installing django-registration is via `pip`,
the standard Python package-installation tool. If you don't have
`pip`, instructions are available for `how to obtain and install it
<https://pip.pypa.io/en/latest/installing.html>`_. If you're using a
supported version of Python, `pip` should have come bundled with
your installation of Python.

Once you have `pip`, type::

    pip install django-registration

If you don't have a copy of a compatible version of Django, this will
also automatically install one for you, and will install a third-party
library required by some of django-registration's validation code.

.. warning:: **Python 2**

   If you are using Python 2, you should install the latest Django
   1.11 release *before* installing django-registration. Later
   versions of Django no longer support Python 2, and installation
   will fail. To install a compatible version of Django for Python 2,
   run `pip install "Django>=1.11,<2.0"`.


Installing from a source checkout
---------------------------------

If you want to work on django-registration, you can obtain a source
checkout.

The development repository for django-registration is at
<https://github.com/ubernostrum/django-registration>. If you have `git
<http://git-scm.com/>`_ installed, you can obtain a copy of the
repository by typing::

    git clone https://github.com/ubernostrum/django-registration.git

From there, you can use git commands to check out the specific
revision you want, and perform an "editable" install (allowing you to
change code as you work on it) by typing::

    pip install -e .


Next steps
----------

To get up and running quickly, check out :ref:`the quick start guide
<quickstart>`. For full documentation, see :ref:`the documentation
index <index>`.