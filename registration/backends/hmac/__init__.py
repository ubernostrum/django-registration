"""
A two-step (signup, then activation) registration workflow, using
HMAC-signed tokens.

To use, include() the provided URLconf --
registration.backends.hmac.urls -- somewhere in your URL
configuration.

For more details, see the documentation in the docs/ directory of the
source-code distribution, or online at
http://django-registration.readthedocs.org/

"""
