.. _install:


Installation guide
==================

Before installing ``django-registration``, you'll need to have a copy
of `Django <https://www.djangoproject.com>`_ already installed. For
information on obtaining and installing Django, consult the `Django
download page <https://www.djangoproject.com/download/>`_, which
offers convenient packaged downloads and installation instructions.

The |version| release of ``django-registration`` supports Django 1.8
and 1.9, on any Python version supported by those versions of Django:

* Django 1.8 suports Python 2.7, 3.3, 3.4 and 3.5.

* Django 1.9 supports Python 2.7, 3.4 and 3.5.

It is expected that ``django-registration`` |version| will also work
with Django 1.10 and Python 3.6 once they are released.

.. important:: **Python 3.2**

   Although Django 1.8 supported Python 3.2 at the time of its
   release, the Python 3.2 series has reached end-of-life, and as a
   result support for Python 3.2 has been dropped from
   ``django-registration`` as of |version|.


Normal installation
-------------------

The preferred method of installing ``django-registration`` is via
``pip``, the standard Python package-installation tool. If you don't
have ``pip``, instructions are available for `how to obtain and
install it <https://pip.pypa.io/en/latest/installing.html>`_. If
you're using Python 2.7.9 or later (for Python 2) or Python 3.4 or
later (for Python 3), ``pip`` came bundled with your installation of
Python.

Once you have ``pip``, simply type::

    pip install django-registration


Manual installation
-------------------

It's also possible to install ``django-registration`` manually. To do
so, obtain the latest packaged version from `the listing on the Python
Package Index
<https://pypi.python.org/pypi/django-registration/>`_. Unpack the
``.tar.gz`` file, and run::

    python setup.py install

Once you've installed ``django-registration``, you can verify
successful installation by opening a Python interpreter and typing
``import registration``.

If the installation was successful, you'll simply get a fresh Python
prompt. If you instead see an ``ImportError``, check the configuration
of your install tools and your Python import path to ensure
``django-registration`` installed into a location Python can import
from.


Installing from a source checkout
---------------------------------

The development repository for ``django-registration`` is at
<https://github.com/ubernostrum/django-registration>. Presuming you
have `git <http://git-scm.com/>`_ installed, you can obtain a copy of
the repository by typing::

    git clone https://github.com/ubernostrum/django-registration.git

From there, you can use normal git commands to check out the specific
revision you want, and install it using ``python setup.py install``.


Next steps
----------

To get up and running quickly, check out :ref:`the quick start guide
<quickstart>`. For full documentation, see :ref:`the documentation
index <index>`.