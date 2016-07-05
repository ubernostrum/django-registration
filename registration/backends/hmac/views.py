"""
A two-step (registration followed by activation) workflow, implemented
by emailing an HMAC-verified timestamped activation token to the user
on signup.

"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing

from registration import signals
from registration.utils import send_user_activation_email
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
    email_subject_template = None
    email_body_template = None
    email_html_body_template = None

    def register(self, form):
        new_user = self.create_inactive_user(form)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def get_success_url(self, user):
        return ('registration_complete', (), {})

    def create_inactive_user(self, form):
        """
        Create the inactive user account and send an email containing
        activation instructions.

        """
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        self.send_activation_email(new_user)

        return new_user

    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.

        """
        return signing.dumps(
            obj=getattr(user, user.USERNAME_FIELD),
            salt=REGISTRATION_SALT
        )

    def get_email_context(self, activation_key):
        """
        Build the template context used for the activation email.

        """
        return {
            'activation_key': activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': get_current_site(self.request)
        }

    def send_activation_email(self, user):
        """
        Send the activation email. The activation key is simply the
        username, signed using TimestampSigner.

        """
        activation_key = self.get_activation_key(user)
        email_ctx = self.get_email_context(activation_key)
        email_ctx.update({
            'user': user
        })

        send_user_activation_email(user, email_ctx,
                                   self.email_subject_template,
                                   self.email_body_template,
                                   self.email_html_body_template)


class ActivationView(BaseActivationView):
    """
    Given a valid activation key, activate the user's
    account. Otherwise, show an error message stating the account
    couldn't be activated.

    """
    def activate(self, *args, **kwargs):
        # This is safe even if, somehow, there's no activation key,
        # because unsign() will raise BadSignature rather than
        # TypeError on a value of None.
        username = self.validate_key(kwargs.get('activation_key'))
        if username is not None:
            user = self.get_user(username)
            if user is not None:
                user.is_active = True
                user.save()
                return user
        return False

    def get_success_url(self, user):
        return ('registration_activation_complete', (), {})

    def validate_key(self, activation_key):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the username if
        valid or ``None`` if not.

        """
        try:
            username = signing.loads(
                activation_key,
                salt=REGISTRATION_SALT,
                max_age=settings.ACCOUNT_ACTIVATION_DAYS * 86400
            )
            return username
        # SignatureExpired is a subclass of BadSignature, so this will
        # catch either one.
        except signing.BadSignature:
            return None

    def get_user(self, username):
        """
        Given the verified username, look up and return the
        corresponding user account if it exists, or ``None`` if it
        doesn't.

        """
        User = get_user_model()
        lookup_kwargs = {
            User.USERNAME_FIELD: username,
            'is_active': False
        }
        try:
            user = User.objects.get(**lookup_kwargs)
            return user
        except User.DoesNotExist:
            return None
