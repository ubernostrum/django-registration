"""
Model and manager used by the model-based activation workflow. If
you're not using that workflow, you should not have 'registration' in
your INSTALLED_APPS.

This is provided primarily for backwards-compatibility with existing
installations; new installs of django-registration should look into
the HMAC activation workflow in registration.backends.hmac, which also
provides a two-step process but requires no models or storage of the
activation key.

"""

import datetime
import hashlib
import re
import textwrap
import warnings

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.encoding import smart_str
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


SHA1_RE = re.compile('^[a-f0-9]{40}$')


class RegistrationManager(models.Manager):
    """
    Custom manager for the ``RegistrationProfile`` model.

    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.

    """
    def activate_user(self, activation_key):
        """
        Validate an activation key and activate the corresponding user
        if valid. Returns the user account on success, ``False`` on
        failure.

        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        if SHA1_RE.search(activation_key.lower()):
            try:
                profile = self.get(activation_key=activation_key)
            except self.model.DoesNotExist:
                return False
            if not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = self.model.ACTIVATED
                profile.save()
                return user
        return False

    def expired(self):
        """
        Query for all profiles which are expired and correspond to
        non-active users.

        """
        warnings.warn(
            textwrap.dedent('''
            The "cleanupregistration" management command, and the
            RegistrationProfile.objects.delete_expired_users() and
            RegistrationProfile.objects.expired() methods, are
            deprecated and will be removed in django-registration 3.0.

            Deployments which need a way to identify and delete
            expired accounts should determine how they wish to do so
            and implement their own methods for this.
            '''),
            DeprecationWarning
        )
        if settings.USE_TZ:
            now = timezone.now()
        else:
            now = datetime.datetime.now()
        return self.exclude(
            models.Q(user__is_active=True) |
            models.Q(activation_key=self.model.ACTIVATED)
            ).filter(
                user__date_joined__lt=now - datetime.timedelta(
                    settings.ACCOUNT_ACTIVATION_DAYS
                )
            )

    @transaction.atomic
    def create_inactive_user(self, form, site, send_email=True):
        """
        Create a new, inactive user, generate a
        ``RegistrationProfile`` and email its activation key to the
        user, returning the new user.

        """
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        registration_profile = self.create_profile(new_user)

        if send_email:
            registration_profile.send_activation_email(site)

        return new_user

    def create_profile(self, user):
        """
        Create a ``RegistrationProfile`` for a given user, and return
        the ``RegistrationProfile``.

        """
        User = get_user_model()
        username = smart_str(getattr(user, User.USERNAME_FIELD))
        hash_input = (get_random_string(5) + username).encode('utf-8')
        activation_key = hashlib.sha1(hash_input).hexdigest()
        return self.create(user=user,
                           activation_key=activation_key)

    @transaction.atomic
    def delete_expired_users(self):
        """
        Remove expired instances of ``RegistrationProfile`` and their
        associated users.

        """
        for profile in self.expired():
            user = profile.user
            profile.delete()
            user.delete()


@python_2_unicode_compatible
class RegistrationProfile(models.Model):
    """
    A model which stores an activation key for use during user account
    registration.

    """
    ACTIVATED = "ALREADY_ACTIVATED"

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                verbose_name=_(u'user'),
                                on_delete=models.CASCADE)
    activation_key = models.CharField(_(u'activation key'), max_length=40)

    objects = RegistrationManager()

    class Meta:
        verbose_name = _(u'registration profile')
        verbose_name_plural = _(u'registration profiles')

    def __str__(self):
        return "Registration information for %s" % smart_str(self.user)

    def activation_key_expired(self):
        """
        Determine whether this ``RegistrationProfile``'s activation
        key has expired, returning a boolean -- ``True`` if the key
        has expired, ``False`` otherwise.

        """
        expiration_date = datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS
        )
        return self.activation_key == self.ACTIVATED or \
            (self.user.date_joined + expiration_date <= timezone.now())
    activation_key_expired.boolean = True

    def send_activation_email(self, site):
        """
        Send an activation email to the user associated with this
        ``RegistrationProfile``.

        """
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'user': self.user,
                    'site': site}
        subject = render_to_string('registration/activation_email_subject.txt',
                                   ctx_dict)
        # Force subject to a single line to avoid header-injection
        # issues.
        subject = ''.join(subject.splitlines())

        message = render_to_string('registration/activation_email.txt',
                                   ctx_dict)

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
