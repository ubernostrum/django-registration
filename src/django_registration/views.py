"""
Base view classes for all registration workflows.

"""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from . import signals
from .exceptions import ActivationError
from .forms import RegistrationForm


class RegistrationView(FormView):
    """
    Base class for user registration views.

    """
    disallowed_url = reverse_lazy('django_registration_disallowed')
    form_class = RegistrationForm
    success_url = None
    template_name = 'django_registration/registration_form.html'

    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.

        """
        if not self.registration_allowed():
            return HttpResponseRedirect(force_text(self.disallowed_url))
        return super(RegistrationView, self).dispatch(*args, **kwargs)

    def get_success_url(self, user=None):
        """
        Return the URL to redirect to after successful redirection.

        """
        # This is overridden solely to allow django-registration to
        # support passing the user account as an argument; otherwise,
        # the base FormMixin implementation, which accepts no
        # arguments, could be called and end up raising a TypeError.
        return super(RegistrationView, self).get_success_url()

    def form_valid(self, form):
        return HttpResponseRedirect(
            self.get_success_url(self.register(form))
        )

    def registration_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.

        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

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
    template_name = 'django_registration/activation_failed.html'

    def get_success_url(self, user=None):
        """
        Return the URL to redirect to after successful redirection.

        """
        return force_text(self.success_url)

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
            extra_context['activation_error'] = {
                'message': e.message,
                'code': e.code,
                'params': e.params
            }
        else:
            signals.user_activated.send(
                sender=self.__class__,
                user=activated_user,
                request=self.request
            )
            return HttpResponseRedirect(
                force_text(
                    self.get_success_url(activated_user)
                )
            )
        context_data = self.get_context_data()
        context_data.update(extra_context)
        return self.render_to_response(context_data)

    def activate(self, *args, **kwargs):
        """
        Implement account-activation logic here.

        """
        raise NotImplementedError
