"""
Viw classes to exercise options of the registration view behavior not
covered by the built-in workflows.

"""

from registration.backends.model_activation.views import ActivationView


class ActivateWithSimpleRedirect(ActivationView):
    def get_success_url(self, user):
        """
        Returns a simple string URL to redirect to on success, rather
        than a (view, args, kwargs) 3-tuple, to test handling of that
        case.

        """
        return '/'
