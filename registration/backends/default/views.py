"""
Backwards-compatible support for importing the model-based activation
workflow's views.

The new location for those views is
registration.backends.model_activation.views. Importing from
registration.backends.default will raise deprecation warnings, and
support for it will be removed in a future release.

"""

import warnings

warnings.warn(
    "registration.backends.default.views is deprecated; "
    "use registration.backends.model_activation.views instead.",
    DeprecationWarning
)

from registration.backends.model_activation import views as new_location

ActivationView = new_location.ActivationView
RegistrationView = new_location.RegistrationView
