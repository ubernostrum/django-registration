"""
Forms used by the two-step activation workflow.

"""

from django import forms
from django.conf import settings
from django.core import signing
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import REGISTRATION_SALT

# pylint: disable=raise-missing-from


class ActivationForm(forms.Form):
    """
    Form for the activation step of the two-step activation workflow.

    This form has one field, the (string) ``activation_key``, which should be an
    HMAC-signed activation-key value containing the username of the account to activate.

    """

    EXPIRED_MESSAGE = _("This account has expired.")
    INVALID_KEY_MESSAGE = _("The activation key you provided is invalid.")

    activation_key = forms.CharField()

    def clean_activation_key(self):
        """
        Validate the signature of the activation key.

        """
        activation_key = self.cleaned_data["activation_key"]
        try:
            username = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400,
            )
            # This is a bit of a hack. Whatever we return here is the value Django will
            # insert into cleaned_data under the name of this field, and although
            # initially it's the activation-key value we here replace it with the
            # username value decoded from that key. This allows the rest of the
            # processing chain to avoid the need to decode the activation key again, but
            # relies on the fact that we only do this when we've fully verified that the
            # activation key was valid -- if it's invalid, cleaned_data will continue to
            # have the raw activation key.
            return username
        except signing.SignatureExpired:
            raise ValidationError(self.EXPIRED_MESSAGE, code="expired")
        except signing.BadSignature:
            raise ValidationError(self.INVALID_KEY_MESSAGE, code="invalid_key")
