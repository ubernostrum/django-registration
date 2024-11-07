.. _install:


Installation
============

django-registration |release| supports Django 4.2, 5.0, and 5.1, and Python 3.9
through 3.12. See `Django's Python support matrix
<https://docs.djangoproject.com/en/dev/faq/install/#what-python-version-can-i-use-with-django>`_
for details of which Python versions are compatible with each version of
Django.


Installing django-registration
------------------------------

To install django-registration, run the following command from a command
prompt/terminal:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m pip install django-registration

.. tab:: Windows

   .. code-block:: shell

      py -m pip install django-registration

This will use ``pip``, the standard Python package-installation tool. If you
are using a supported version of Python, your installation of Python should
have come with ``pip`` bundled. If ``pip`` does not appear to be present, you
can try running the following from a command prompt/terminal:

.. tab:: macOS/Linux/other Unix

   .. code-block:: shell

      python -m ensurepip --upgrade

.. tab:: Windows

   .. code-block:: shell

      py -m ensurepip --upgrade

Instructions are also available for `how to obtain and manually install or
upgrade pip <https://pip.pypa.io/en/latest/installation/>`_.

If you don't already have a supported version of Django installed, using
``pip`` to install django-registration will also install the latest
supported version of Django.


Next steps
----------

To get up and running quickly, check out :ref:`the quick start guide
<quickstart>`. For full documentation, see :ref:`the documentation
index <index>`.
