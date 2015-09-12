import warnings

warnings.warn(
    "registration.backends.default is deprecated; "
    "use registration.backends.model_activation instead.",
    DeprecationWarning
)

from registration.backends.model_activation.views import ActivationView
from registration.backends.model_activation.views import RegistrationView
