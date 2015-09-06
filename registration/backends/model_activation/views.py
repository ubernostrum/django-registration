"""
A two-step (registration followed by activation) workflow, implemented
by storing an activation key in a model and emailing the key to the
user.

This workflow is provided primarily for backwards-compatibility with
existing installations; new installs of django-registration should
look into the HMAC activation workflow in registration.backends.hmac.

"""

from django.apps import apps
from django.contrib.sites.requests import RequestSite
from django.contrib.sites.models import Site

from registration import signals
from registration.models import RegistrationProfile
from registration.views import ActivationView as BaseActivationView
from registration.views import RegistrationView as BaseRegistrationView


class RegistrationView(BaseRegistrationView):
    """
    Register a new (inactive) user account, generate and store an
    activation key, and email it to the user.

    """
    def register(self, **cleaned_data):
        if apps.is_installed('django.contrib.sites'):
            site = Site.objects.get_current()
        else:
            site = RequestSite(self.request)
        new_user = RegistrationProfile.objects.create_inactive_user(
            site=site,
            **self.get_user_kwargs(**cleaned_data)
        )
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def get_success_url(self, user):
        return ('registration_complete', (), {})


class ActivationView(BaseActivationView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.

    """
    def activate(self, *args, **kwargs):
        activation_key = kwargs.get('activation_key')
        activated_user = RegistrationProfile.objects.activate_user(
            activation_key
        )
        return activated_user

    def get_success_url(self, user):
        return ('registration_activation_complete', (), {})
