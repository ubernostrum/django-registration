"""
Backwards-compatible support for include()-ing the model-based
activation workflow's URLconf.

The new location for that URLconf is
registration.backends.model_activation.urls. Using include() with
registration.backends.default.urls will raise deprecation warnings,
and support for it will be removed in a future release.

"""

import warnings

from registration.backends.model_activation import urls as model_urls


warnings.warn(
    "registration.backends.default.urls is deprecated; "
    "use registration.backends.model_activation.urls instead.",
    DeprecationWarning
)


urlpatterns = model_urls.urlpatterns
