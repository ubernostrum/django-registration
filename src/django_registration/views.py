"""
Base view classes for all registration workflows.

"""

# SPDX-License-Identifier: BSD-3-Clause

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.edit import FormView

from . import signals
from .exceptions import ActivationError
from .forms import RegistrationForm

USER_MODEL_MISMATCH = """You are attempting to use the registration view {view} with
the form class {form}, but the model used by that form ({form_model}) is not your Django
installation's user model ({user_model}).

Check your form's Meta declaration to ensure it is using the correct user model."""


class RegistrationView(FormView):
    """
    Base class for user registration views.

    This is a :class:`~django.views.generic.edit.FormView`, so any attributes/methods
    which can be overridden on ``FormView`` can also be overridden here.

    One custom method here *must* be implemented by subclasses:

    .. automethod:: register

    Useful optional places to override or customize on subclasses are:

    .. automethod:: registration_allowed

    .. attribute:: disallowed_url

       The URL to redirect to when registration is disallowed. Can be a hard-coded
       string, the string resulting from calling Django's :func:`~django.urls.reverse`
       helper, or the lazy object produced by Django's :func:`~django.urls.reverse_lazy`
       helper. Default value is the result of calling :func:`~django.urls.reverse_lazy`
       with the URL name ``'registration_disallowed'``.

    .. attribute:: form_class

       The form class to use for user registration. Can be overridden on a per-request
       basis (see below). Should be the actual class object; by default, this class is
       :class:`django_registration.forms.RegistrationForm`.

    .. attribute:: success_url

       The URL to redirect to after successful registration. Can be a hard-coded string,
       the string resulting from calling Django's :func:`~django.urls.reverse` helper,
       or the lazy object produced by Django's :func:`~django.urls.reverse_lazy`
       helper. Can be overridden on a per-request basis (see below). Default value is
       :data:`None`; subclasses must override and provide this.

    .. attribute:: template_name

       The template to use for user registration. Should be a string. Default value is
       ``'django_registration/registration_form.html'``.

    .. method:: get_form_class()

       Select a form class to use on a per-request basis. If not overridden, will use
       :attr:`~form_class`. Should be the actual class object.

       :rtype: django_registration.forms.RegistrationForm

    .. method:: get_success_url(user)

       Return a URL to redirect to after successful registration, on a per-request or
       per-user basis. If not overridden, will use :attr:`~success_url`. Should return a
       value of the same type as :attr:`success_url` (see above).

       :param django.contrib.auth.models.AbstractUser user: The new user account.
       :rtype: str

    """

    disallowed_url = reverse_lazy("django_registration_disallowed")
    form_class = RegistrationForm
    success_url = None
    template_name = "django_registration/registration_form.html"

    @method_decorator(sensitive_post_parameters())
    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to dispatch or do
        other processing.

        """
        if not self.registration_allowed():
            return HttpResponseRedirect(force_str(self.disallowed_url))
        return super().dispatch(*args, **kwargs)

    def get_form(self, form_class=None):
        """
        Returns an instance of the form to be used in this view.

        This is an override of the base version of this method in Django's FormMixin, to
        immediately and loudly break if the model of this view's form class is not the
        user model Django has been configured to use.

        Most often this will be the case because Django has been configured to use a
        custom user model, but the developer has forgotten to also configure an
        appropriate custom registration form to match it.

        """
        # pylint: disable=protected-access
        if form_class is None:  # pragma: no cover
            form_class = self.get_form_class()
        form_model = form_class._meta.model
        user_model = get_user_model()
        if form_model._meta.label != user_model._meta.label:
            raise ImproperlyConfigured(
                USER_MODEL_MISMATCH.format(
                    view=self.__class__,
                    form=form_class,
                    form_model=form_model,
                    user_model=user_model,
                )
            )
        return form_class(**self.get_form_kwargs())

    def get_success_url(self, user=None):  # pylint: disable=unused-argument
        """
        Return the URL to redirect to after successful redirection.

        """
        # This is overridden solely to allow django-registration to support passing the
        # user account as an argument; otherwise, the base FormMixin implementation,
        # which accepts no arguments, could be called and end up raising a TypeError.
        return super().get_success_url()

    def form_valid(self, form):
        """
        After successful form processing, redirect to the success URL.

        """
        return HttpResponseRedirect(self.get_success_url(self.register(form)))

    def registration_allowed(self):
        """
        Indicate whether user registration is allowed, either in general or for this
        specific request. Default value is the value of the setting
        ``REGISTRATION_OPEN``.

        :rtype: bool

        """
        return getattr(settings, "REGISTRATION_OPEN", True)

    def register(self, form):
        """
        Subclasses *must* override this method.

        Implement your registration logic here. ``form`` will be the
        (already-validated) form filled out by the user during the registration process
        (i.e., a valid instance of :class:`~django_registration.forms.RegistrationForm`
        or a subclass of it).

        This method should return the newly-registered user instance, and should send
        the signal :data:`django_registration.signals.user_registered`. Note that this
        is not automatically done for you when writing your own custom subclass, so you
        must send this signal manually.

        :param django_registration.forms.RegistrationForm form: The registration form to use.
        :rtype: django.contrib.auth.models.AbstractUser

        """
        raise NotImplementedError(
            "Subclasses of RegistrationView must implement register()."
        )


class ActivationView(FormView):
    """
    Base class for user activation views.

    This is a :class:`~django.views.generic.edit.FormView`, so any attributes/methods
    which can be overridden on ``FormView`` can also be overridden here.

    There are two opportunities to raise errors here: they can be raised as validation
    errors in the form, or raised via
    :exc:`~django_registration.exceptions.ActivationError` in your :meth:`activate`
    method. In the latter case, the exception's ``message``, ``code``, and ``params``
    will be gathered into a dictionary and injected into the template context as the
    variable ``activation_error``.

    Two custom methods *must* be implemented by subclasses:

    .. automethod:: activate

    .. automethod:: get_activation_data

    Useful places to override or customize on a subclass are:

    .. attribute:: success_url

       The URL to redirect to after successful activation. Can be a hard-coded string,
       the string resulting from calling Django's :func:`~django.urls.reverse` helper,
       or the lazy object produced by Django's :func:`~django.urls.reverse_lazy`
       helper. Can be overridden on a per-request basis (see below). Default value is
       :data:`None`; subclasses must override and provide this.

    .. attribute:: template_name

       The template to use on HTTP ``GET`` and on activation failures. Should be a
       string. Default value is ``'django_registration/activation_form.html'``.

    .. method:: get_success_url(user)

       Return a URL to redirect to after successful activation, on a per-request or
       per-user basis. If not overridden, will use :attr:`~success_url`. Should return a
       value of the same type as :attr:`success_url` (see above).

       :param django.contrib.auth.models.AbstractUser user: The activated user account.
       :rtype: str

    """

    success_url = None
    template_name = "django_registration/activation_form.html"

    def get_initial(self):
        """
        Return the initial data used for the activation form.

        This is overridden to allow our view to introduce a standard method name
        specifically for getting activation data.

        """
        initial = super().get_initial()
        initial.update(self.get_activation_data(self.request))
        return initial

    def get_success_url(self, user=None):  # pylint: disable=unused-argument
        """
        Return the URL to redirect to after successful redirection.

        """
        # This is overridden solely to allow django-registration to support passing the
        # user account as an argument; otherwise, the base FormMixin implementation,
        # which accepts no arguments, could be called and end up raising a TypeError.
        return force_str(self.success_url)

    def form_valid(self, form):
        """
        If the form is valid, attempt to activate the user account and redirect to
        the succeess URL. If an :class:`~django_registration.exceptions.ActivationError`
        is raised during activation, instead re-render the form and include information
        about the error in the template context.

        """
        extra_context = {}
        try:
            activated_user = self.activate(form)
        except ActivationError as exc:
            extra_context["activation_error"] = {
                "message": exc.message,
                "code": exc.code,
                "params": exc.params,
            }
        else:
            signals.user_activated.send(
                sender=self.__class__, user=activated_user, request=self.request
            )
            return HttpResponseRedirect(
                force_str(self.get_success_url(user=activated_user))
            )
        context_data = self.get_context_data()
        context_data.update(extra_context)
        return self.render_to_response(context_data)

    def activate(self, form):
        """
        Subclasses *must* override this method.

        Attempt to activate the user account from the given form. Should either return
        the activated user account, or raise
        :exc:`~django_registration.exceptions.ActivationError`.

        """
        raise NotImplementedError(
            "Subclasses of ActivationView must implement activate()."
        )

    def get_activation_data(self, request):
        """
        Subclasses *must* override this method.

        Return the initial activation data for populating the activation form (for
        example, by reading an activation key from a querystring parameter)

        """
        raise NotImplementedError(
            "Subclasses of ActivationView must implement get_activation_data()."
        )
