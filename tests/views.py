"""
Viw classes to exercise options of the registration view behavior not
covered by the built-in workflows.

"""
from django.urls import reverse_lazy

from django_registration.backends.hmac.views import ActivationView


class ActivateWithComplexRedirect(ActivationView):
    success_url = reverse_lazy('registration_activation_complete')
