"""
Custom signals sent during the registration and activation processes.

"""

from django.dispatch import Signal


# A new user has registered.
user_registered = Signal(providing_args=["user", "request"])

# A user has activated his or her account.
user_activated = Signal(providing_args=["user", "request"])

# A user activation failed.
user_activation_failed = Signal(providing_args=["request"])
