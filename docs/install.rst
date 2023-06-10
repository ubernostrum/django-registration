.. _install:


Installation and recommended configuration
==========================================

django-registration |release| supports Django 3.2, 4.1, and 4.2 on Python 3.7
(Django 3.2 only), 3.8, 3.9, 3.10, and 3.11 (Django 4.1 and 4.2 only). Note
that Django 3.2's support for Python 3.10 was added in Django 3.2.9, so you may
experience issues with Python 3.10 and earlier Django 3.2 versions.

.. note:: **Django 3.2 and supported Python versions**

   Django 3.2 was released before Python 3.10 had come out, and although it now
   supports Python 3.10, it did not officially do so until the Django 3.2.9
   release. You may encounter problems if you try to use Django 3.2.8 or
   earlier with Python 3.10.

   Also, although Django 3.2 continues to officially support Python 3.6,
   django-registration |release| does not, because the Python core team's
   support window for Python 3.6 ended in December 2021.


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
