.. _faq:

Frequently-asked questions
==========================

The following are miscellaneous common questions and answers related
to installing/using django-registration, culled from bug reports,
emails and other sources.


General
-------

**What license is django-registration under?**

    ``django-registration`` is offered under a three-clause BSD-style
    license; this is `an OSI-approved open-source license
    <http://www.opensource.org/licenses/bsd-license.php>`_, and allows
    you a large degree of freedom in modifiying and redistributing the
    code. For the full terms, see the file ``LICENSE`` which came with
    your copy of django-registration; if you did not receive a copy of
    this file, you can view it online at
    <https://github.com/ubernostrum/django-registration/blob/master/LICENSE>.

**What versions of Django and Python are supported?**

    As of ``django-registration`` |version|, Django 1.7 and 1.8 are
    supported, on any of Python 2.7, 3.3 or 3.4. It is anticipated
    that ``django-registration`` will also work with Python 3.5 once
    Python 3.5 is released.

**I found a bug or want to make an improvement!**

    The canonical development repository for ``django-registration``
    is online at
    <https://github.com/ubernostrum/django-registration>. Issues and
    pull requests can both be filed there.


Installation and setup
----------------------

**How do I install django-registration?**

    Full instructions are available in :ref:`the quick start guide <quickstart>`.

**Does django-registration come with any sample templates I can use right away?**
    No, for two reasons:

    1. Providing default templates with an application is generally
       hard to impossible, because different sites can have such
       wildly different design and template structure. Any attempt to
       provide templates which would work with all the possibilities
       would probably end up working with none of them.

    2. A number of things in django-registration depend on the
       specific registration workflow you use, including the variables
       which end up in template contexts. Since django-registration
       has no way of knowing in advance what workflow you're going to
       be using, it also has no way of knowing what your templates
       will need to look like.
    
    Fortunately, however, django-registration has good documentation
    which explains what context variables will be available to
    templates, and so it should be easy for anyone who knows Django's
    template system to create templates which integrate with their own
    site.


Configuration
-------------

**Do I need to rewrite the views to change the way they behave?**

    Not always. Any behavior controlled by an attribute on a
    class-based view can be changed by passing a different value for
    that attribute in the URLConf. See `Django's class-based view
    documentation
    <https://docs.djangoproject.com/en/1.8/topics/class-based-views/#simple-usage-in-your-urlconf>`_
    for examples of this.

    For more complex or fine-grained control, you will likely want to
    subclass :class:`~registration.views.RegistrationView` or
    :class:`~registration.views.ActivationView`, or both, add your
    custom logic to your subclasses, and then create a URLConf which
    makes use of your subclasses.
    
**I don't want to write my own URLconf because I don't want to write patterns for all the auth views!**

    You're in luck, then; django-registration provides a URLconf which
    *only* contains the patterns for the auth views, and which you can
    include in your own URLconf anywhere you'd like; it lives at
    ``registration.auth_urls``.

**I don't like the names you've given to the URL patterns!**

    In that case, you should feel free to set up your own URLconf
    which uses the names you want.

**I'm using a custom user model; how do I make that work?**

    See :ref:`the custom user documentation <custom-user>`.

Tips and tricks
---------------

**How do I log a user in immediately after registration or activation?**

    Take a look at the implementation of :ref:`the simple one-step workflow
    <simple-workflow>`, which logs a user in immediately after
    registration.


**How do I re-send an activation email?**

    Assuming you're using :ref:`the default workflow
    <default-workflow>`, a `custom admin action
    <http://docs.djangoproject.com/en/1.8/ref/contrib/admin/actions/>`_
    is provided for this; in the admin for the
    :class:`~registration.models.RegistrationProfile` model, simply
    click the checkbox for the user(s) you'd like to re-send the email
    for, then select the "Re-send activation emails" action.

**How do I manually activate a user?**

    In the default workflow, a custom admin action is provided for
    this. In the admin for the ``RegistrationProfile`` model, click
    the checkbox for the user(s) you'd like to activate, then select
    the "Activate users" action.