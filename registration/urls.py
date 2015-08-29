"""
Backwards-compatible URLconf for existing django-registration
installs; this allows the standard ``include('registration.urls')`` to
continue working, but that usage is deprecated and will be removed for
django-registration 1.9. For new installs, use
``include('registration.backends.model_activation.urls')``.

"""

import warnings

warnings.warn(
    "include('registration.urls') is deprecated; use "
    "include('registration.backends.model_activation.urls') instead.",
    DeprecationWarning
)

from registration.backends.model_activation import urls as model_urls

urlpatterns = model_urls.urlpatterns
