"""
Viw classes to exercise options of the registration view behavior not
covered by the built-in workflows.

"""

from registration.backends.model_activation.views import ActivationView


class ActivateWithComplexRedirect(ActivationView):
    success_url = ('registration_activation_complete', (), {})
