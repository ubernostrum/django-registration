"""
Backwards-compatible support for importing the model-based activation
workflow's views.

The new location for those views is
registration.backends.model_activation.views. Importing from
registration.backends.default will raise deprecation warnings, and
support for it will be removed in a future release.

"""

import textwrap
import warnings

from registration.backends.model_activation import views as new_location


warnings.warn(
    textwrap.dedent("""
        registration.backends.default.views is deprecated and
        will be removed in django-registration 3.0. Import from
        registration.backends.model_activation.views
        instead.
    """),
    DeprecationWarning
)


ActivationView = new_location.ActivationView
RegistrationView = new_location.RegistrationView
