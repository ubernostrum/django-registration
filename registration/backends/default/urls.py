import warnings

warnings.warn(
    "registration.backends.default is deprecated; "
    "use registration.backends.model_activation instead.",
    DeprecationWarning
)

from registration.backends.model_activation import urls as model_urls

urlpatterns = model_urls.urlpatterns
