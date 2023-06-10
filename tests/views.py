"""
Viw classes to exercise options of the registration view behavior not
covered by the built-in workflows.

"""
from django.urls import reverse_lazy

from django_registration.backends.activation.views import ActivationView


class ActivateWithComplexRedirect(ActivationView):
    """
    An activation view with a ``success_url`` more complex than a simple string.

    """

    success_url = reverse_lazy("django_registration_activation_complete")
