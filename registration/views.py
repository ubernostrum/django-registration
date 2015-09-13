"""
Base view classes for all registration workflows.

"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from registration import signals
from registration.forms import RegistrationForm


class RegistrationView(FormView):
    """
    Base class for user registration views.

    """
    disallowed_url = 'registration_disallowed'
    form_class = RegistrationForm
    success_url = None
    template_name = 'registration/registration_form.html'

    def dispatch(self, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.

        """
        if not self.registration_allowed():
            return redirect(self.disallowed_url)
        return super(RegistrationView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        new_user = self.register(**form.cleaned_data)
        success_url = self.get_success_url(new_user)

        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)

    def registration_allowed(self):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.

        By default, uses the value of the setting
        ``REGISTRATION_OPEN``, as follows:

        * If ``REGISTRATION_OPEN`` is not specified in settings, or is
          set to ``True``, registration is permitted.

        * If ``REGISTRATION_OPEN`` is both specified and set to
          ``False``, registration is not permitted.

        """
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def register(self, **cleaned_data):
        """
        Implement user-registration logic here. Access to both the
        request and the full cleaned_data of the registration form is
        available here.

        """
        raise NotImplementedError

    def get_user_kwargs(self, **cleaned_data):
        """
        Given the cleaned_data from the registration form, return from
        them a dictionary of keyword arguments which can be passed to
        ``create_user()``. By default, this is a dictionary with
        values for User.USERNAME_FIELD, email, and password, to match
        the signature of Django's default User implementation, and
        assumes the field names of the default RegistrationForm class.

        """
        User = get_user_model()
        return {
            User.USERNAME_FIELD: cleaned_data['username'],
            'email': cleaned_data['email'],
            'password': cleaned_data['password1'],
        }


class ActivationView(TemplateView):
    """
    Base class for user activation views.

    """
    template_name = 'registration/activate.html'

    def get(self, *args, **kwargs):
        activated_user = self.activate(*args, **kwargs)
        if activated_user:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated_user,
                                        request=self.request)
            success_url = self.get_success_url(activated_user)
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        return super(ActivationView, self).get(*args, **kwargs)

    def activate(self, *args, **kwargs):
        """
        Implement account-activation logic here.

        """
        raise NotImplementedError

    def get_success_url(self, user):
        raise NotImplementedError
