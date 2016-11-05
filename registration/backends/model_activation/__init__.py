"""
A two-step (signup, then activation) registration workflow, using
a model to store the activation key.

To use, add 'registration' to your INSTALLED_APPS, run migrations and
include() the provided URLconf --
registration.backends.model_activation.urls -- somewhere in your URL
configuration.

For more details, see the documentation in the docs/ directory of the
source-code distribution, or online at
https://django-registration.readthedocs.io/

"""
