"""
Some exceptions class that can be used to catch common errors
"""


class BadActivationKey(Exception):
    pass


class ActivationKeyExpired(Exception):
    pass
