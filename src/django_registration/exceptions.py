"""
Exception classes used in registration workflows.

"""


class RegistrationError(Exception):
    """
    Base class for registration errors.

    """
    def __init__(self, message, code=None, params=None):
        super(RegistrationError, self).__init__(message, code, params)
        self.message = message
        self.code = code
        self.params = params


class ActivationError(RegistrationError):
    """
    Base class for account-activation errors.

    """
    pass
