"""
Backwards-compatible URLconf for existing django-registration
installs; this allows the standard ``include('registration.urls')`` to
continue working, but that usage is deprecated and will be removed in
django-registration 3.0.  For new installs, use
``include('registration.backends.model_activation.urls')``.

"""

import textwrap
import warnings

from registration.backends.model_activation import urls as model_urls


warnings.warn(
    textwrap.dedent("""
        include('registration.urls') is deprecated and will be removed in
        django-registration 3.0. Use
        include('registration.backends.model_activation.urls')
        instead.
    """),
    DeprecationWarning
)


urlpatterns = model_urls.urlpatterns
