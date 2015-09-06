"""
A two-step (registration followed by activation) workflow, implemented
by emailing an HMAC-verified timestamped activation token to the user
on signup.

"""
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.requests import RequestSite
from django.contrib.sites.models import Site
from django.core import signing
from django.template.loader import render_to_string

from registration import signals
from registration.views import ActivationView as BaseActivationView
from registration.views import RegistrationView as BaseRegistrationView


REGISTRATION_SALT = getattr(settings, 'REGISTRATION_SALT', 'registration')


class RegistrationView(BaseRegistrationView):
    """
    Register a new (inactive) user account, generate an activation key
    and email it to the user.

    This is different from the model-based activation workflow in that
    the activation key is simply the username, signed using Django's
    TimestampSigner, with HMAC verification on activation.

    """
    email_body_template = 'registration/activation_email.txt'
    email_subject_template = 'registration/activation_email_subject.txt'

    def register(self, **cleaned_data):
        new_user = self.create_inactive_user(
            **self.get_user_kwargs(**cleaned_data)
        )
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def get_success_url(self, user):
        return ('registration_complete', (), {})

    def create_inactive_user(self, username, email, password):
        """
        Create the inactive user account and send an email containing
        activation instructions.

        """
        User = get_user_model()
        user_kwargs = {
            User.USERNAME_FIELD: username,
            'email': email,
            'password': password,
        }
        new_user = User.objects.create_user(**user_kwargs)
        new_user.is_active = False
        new_user.save()

        self.send_activation_email(new_user)

        return new_user

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is simply the
        username, signed using TimestampSigner.

        """
        User = get_user_model()
        signer = signing.TimestampSigner(salt=REGISTRATION_SALT)
        activation_key = signer.sign(
            str(getattr(user, User.USERNAME_FIELD))
        )

        if apps.is_installed('django.contrib.sites'):
            site = Site.objects.get_current()
        else:
            site = RequestSite(self.request)

        context = {
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': site,
        }
        subject = render_to_string(self.email_subject_template,
                                   context)
        subject = ''.join(subject.splitlines())
        message = render_to_string(self.email_body_template,
                                   context)
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


class ActivationView(BaseActivationView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.

    """
    def activate(self, *args, **kwargs):
        activation_key = kwargs.get('activation_key')
        username = None
        signer = signing.TimestampSigner(salt=REGISTRATION_SALT)

        try:
            username = signer.unsign(
                activation_key,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
        # SignatureExpired is a subclass of BadSignature, so this will
        # catch either one.
        except signing.BadSignature:
            return False

        User = get_user_model()
        lookup_kwargs = {
            User.USERNAME_FIELD: username
        }
        try:
            user = User.objects.get(**lookup_kwargs)
        except User.DoesNotExist:
            return False

        user.is_active = True
        user.save()
        return user

    def get_success_url(self, user):
        return ('registration_activation_complete', (), {})
