"""
Viw classes to exercise options of the registration view behavior not
covered by the built-in workflows.

"""

from django_registration.backends.hmac.views import ActivationView


class ActivateWithComplexRedirect(ActivationView):
    success_url = ('registration_activation_complete', (), {})
