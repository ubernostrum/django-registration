"""
Base view classes for all registration workflows.

"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.encoding import force_str
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from . import signals
from .exceptions import ActivationError
from .forms import RegistrationForm

USER_MODEL_MISMATCH = """
You are attempting to use the registration view {view}
with the form class {form},
but the model used by that form ({form_model}) is not
your Django installation's user model ({user_model}).

Most often this occurs because you are using a custom user model, but
forgot to specify a custom registration form class for it. Specifying
a custom registration form class is required when using a custom user
model. Please see django-registration's documentation on custom user
models for more details.
"""


class RegistrationView(FormView):
    """
    Base class for user registration views.

    """

    disallowed_url = reverse_lazy("django_registration_disallowed")
    form_class = RegistrationForm
    success_url = None
    template_name = "django_registration/registration_form.html"

    @method_decorator(sensitive_post_parameters())
    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.

        """
        if not self.registration_allowed():
            return HttpResponseRedirect(force_str(self.disallowed_url))
        return super().dispatch(*args, **kwargs)

    def get_form(self, form_class=None):
        """
        Returns an instance of the form to be used in this view.

        This is an override of the base version of this method in
        Django's FormMixin, to immediately and loudly break if the
        model of this view's form class is not the user model Django
        has been configured to use.

        Most often this will be the case because Django has been
        configured to use a custom user model, but the developer has
        forgotten to also configure an appropriate custom registration
        form to match it.

        """
        if form_class is None:
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

    def get_success_url(self, user=None):
        """
        Return the URL to redirect to after successful redirection.

        """
        # This is overridden solely to allow django-registration to
        # support passing the user account as an argument; otherwise,
        # the base FormMixin implementation, which accepts no
        # arguments, could be called and end up raising a TypeError.
        return super().get_success_url()

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url(self.register(form)))

    def registration_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.

        """
        return getattr(settings, "REGISTRATION_OPEN", True)

    def register(self, form):
        """
        Implement user-registration logic here. Access to both the
        request and the registration form is available here.

        """
        raise NotImplementedError


class ActivationView(TemplateView):
    """
    Base class for user activation views.

    """

    success_url = None
    template_name = "django_registration/activation_failed.html"

    def get_success_url(self, user=None):
        """
        Return the URL to redirect to after successful redirection.

        """
        return force_str(self.success_url)

    def get(self, *args, **kwargs):
        """
        The base activation logic; subclasses should leave this method
        alone and implement activate(), which is called from this
        method.

        """
        extra_context = {}
        try:
            activated_user = self.activate(*args, **kwargs)
        except ActivationError as e:
            extra_context["activation_error"] = {
                "message": e.message,
                "code": e.code,
                "params": e.params,
            }
        else:
            signals.user_activated.send(
                sender=self.__class__, user=activated_user, request=self.request
            )
            return HttpResponseRedirect(force_str(self.get_success_url(activated_user)))
        context_data = self.get_context_data()
        context_data.update(extra_context)
        return self.render_to_response(context_data)

    def activate(self, *args, **kwargs):
        """
        Implement account-activation logic here.

        """
        raise NotImplementedError
