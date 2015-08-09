"""
Exercise options of the registration view behavior not covered by the
built-in backends.

"""

from registration.backends.default.views import ActivationView


class ActivateWithSimpleRedirect(ActivationView):
    def get_success_url(self, user):
        """
        Returns a simple string URL to redirect to on success, rather
        than a (view, args, kwargs) 3-tuple, to test handling of that
        case.

        """
        return '/'
