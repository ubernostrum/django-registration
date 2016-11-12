"""
Tests for the model and manager in the model-based workflow.

"""

import datetime
import hashlib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail, management
from django.db import models
from django.test import RequestFactory, TestCase, override_settings
from django.utils.six import text_type

from ..forms import RegistrationForm
from ..models import SHA1_RE, RegistrationProfile


User = get_user_model()


@override_settings(ACCOUNT_ACTIVATION_DAYS=7)
class RegistrationModelTests(TestCase):
    """
    Test the model and manager used in the model-based activation
    workflow.

    """
    user_info = {
        User.USERNAME_FIELD: 'alice',
        'password': 'swordfish',
        'email': 'alice@example.com'
    }

    user_lookup_kwargs = {
        User.USERNAME_FIELD: 'alice'
    }

    def get_form(self):
        """
        Create and return a RegistrationForm filled with valid data.

        """
        form = RegistrationForm(
            data={
                User.USERNAME_FIELD: 'alice',
                'password1': 'swordfish',
                'password2': 'swordfish',
                'email': 'alice@example.com',
            }
        )
        return form

    def get_site(self):
        """
        Return a Site or RequestSite instance for use in registration.

        """
        factory = RequestFactory()
        return get_current_site(factory.get('/'))

    def test_profile_creation(self):
        """
        Creating a registration profile for a user populates the
        profile with the correct user and a SHA1 hash to use as
        activation key.

        """
        new_user = User.objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertEqual(profile.user.id, new_user.id)
        self.assertTrue(SHA1_RE.match(profile.activation_key))
        self.assertEqual(
            text_type(profile),
            "Registration information for %s" % (
                self.user_info[User.USERNAME_FIELD]
            )
        )

    def test_activation_email(self):
        """
        RegistrationProfile.send_activation_email sends an email.

        """
        new_user = User.objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)
        profile.send_activation_email(self.get_site())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    def test_user_creation(self):
        """
        Creating a new user populates the correct data, and sets the
        user's account inactive.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            self.get_form(),
            site=self.get_site()
        )
        self.assertEqual(
            getattr(new_user, User.USERNAME_FIELD),
            self.user_info[User.USERNAME_FIELD]
        )
        self.assertEqual(
            new_user.email, self.user_info['email']
        )
        self.assertTrue(
            new_user.check_password(self.user_info['password'])
        )
        self.assertFalse(new_user.is_active)

    def test_user_creation_email(self):
        """
        By default, creating a new user sends an activation email.

        """
        RegistrationProfile.objects.create_inactive_user(
            self.get_form(),
            site=self.get_site()
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_user_creation_no_email(self):
        """
        Passing send_email=False when creating a new user doesn't send
        an activation email.

        """
        RegistrationProfile.objects.create_inactive_user(
            form=self.get_form(),
            site=self.get_site(),
            send_email=False,
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_unexpired_account(self):
        """
        RegistrationProfile.activation_key_expired() is False within
        the activation window.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            self.get_form(),
            site=self.get_site()
        )
        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertFalse(profile.activation_key_expired())

    def test_expired_account(self):
        """
        RegistrationProfile.activation_key_expired() is True outside
        the activation window.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            self.get_form(),
            site=self.get_site()
        )
        new_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1
        )
        new_user.save()
        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertTrue(profile.activation_key_expired())

    def test_valid_activation(self):
        """
        Activating a user within the permitted window makes the
        account active, and resets the activation key.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            form=self.get_form(),
            site=self.get_site()
        )
        profile = RegistrationProfile.objects.get(user=new_user)
        activated = RegistrationProfile.objects.activate_user(
            profile.activation_key
        )

        self.assertTrue(isinstance(activated, User))
        self.assertEqual(activated.id, new_user.id)
        self.assertTrue(activated.is_active)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertEqual(profile.activation_key, RegistrationProfile.ACTIVATED)

    def test_expired_activation(self):
        """
        Attempting to activate outside the permitted window doesn't
        activate the account.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            form=self.get_form(),
            site=self.get_site()
        )
        new_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1
        )
        new_user.save()

        profile = RegistrationProfile.objects.get(user=new_user)
        activated = RegistrationProfile.objects.activate_user(
            profile.activation_key
        )

        self.assertFalse(isinstance(activated, User))
        self.assertFalse(activated)

        new_user = User.objects.get(**self.user_lookup_kwargs)
        self.assertFalse(new_user.is_active)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertNotEqual(
            profile.activation_key,
            RegistrationProfile.ACTIVATED
        )

    def test_activation_invalid_key(self):
        """
        Attempting to activate with a key which is not a SHA1 hash
        fails.

        """
        self.assertFalse(RegistrationProfile.objects.activate_user('foo'))

    def test_activation_already_activated(self):
        """
        Attempting to re-activate an already-activated account fails.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            form=self.get_form(),
            site=self.get_site()
        )
        profile = RegistrationProfile.objects.get(user=new_user)
        RegistrationProfile.objects.activate_user(profile.activation_key)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertFalse(
            RegistrationProfile.objects.activate_user(
                profile.activation_key
            )
        )

    def test_activation_nonexistent_key(self):
        """
        Attempting to activate with a non-existent key (i.e., one not
        associated with any account) fails.

        """
        # Due to the way activation keys are constructed during
        # registration, this will never be a valid key.
        invalid_key = hashlib.sha1('foo'.encode('utf-8')).hexdigest()
        self.assertFalse(
            RegistrationProfile.objects.activate_user(
                invalid_key
            )
        )

    def test_expired_user_deletion(self):
        """
        RegistrationProfile.objects.delete_expired_users() only
        deletes inactive users whose activation window has expired.

        """
        RegistrationProfile.objects.create_inactive_user(
            form=self.get_form(),
            site=self.get_site()
        )

        expired_form = RegistrationForm(
            data={
                User.USERNAME_FIELD: 'bob',
                'password1': 'swordfish',
                'password2': 'swordfish',
                'email': 'bob@example.com',
            }
        )
        expired_user = RegistrationProfile.objects.create_inactive_user(
            form=expired_form,
            site=self.get_site()
        )
        expired_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1
        )
        expired_user.save()

        RegistrationProfile.objects.delete_expired_users()
        self.assertEqual(1, RegistrationProfile.objects.count())
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(**{
                User.USERNAME_FIELD: 'bob'
            })

    def test_management_command(self):
        """
        The cleanupregistration management command properly deletes
        expired accounts.

        """
        RegistrationProfile.objects.create_inactive_user(
            form=self.get_form(),
            site=self.get_site()
        )
        expired_form = RegistrationForm(
            data={
                User.USERNAME_FIELD: 'bob',
                'password1': 'swordfish',
                'password2': 'swordfish',
                'email': 'bob@example.com',
            }
        )
        expired_user = RegistrationProfile.objects.create_inactive_user(
            form=expired_form,
            site=self.get_site()
        )
        expired_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1
        )
        expired_user.save()

        management.call_command('cleanupregistration')
        self.assertEqual(RegistrationProfile.objects.count(), 1)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(**{
                User.USERNAME_FIELD: 'bob'
            })

    def test_expired_query(self):
        """
        The expired() method of RegistrationManager correctly returns
        only expired registration profiles.

        """
        form = RegistrationForm(
            data={
                User.USERNAME_FIELD: 'test_expired_query',
                'password1': 'swordfish',
                'password2': 'swordfish',
                'email': 'test_expired_query@example.com'
            }
        )
        user = RegistrationProfile.objects.create_inactive_user(
            form=form,
            site=self.get_site()
        )
        profile = RegistrationProfile.objects.get(user=user)
        original_date_joined = user.date_joined
        original_activation_key = profile.activation_key

        # Test matrix for expired() is as follows:
        #
        # * User with is_active=False, activation_key != ACTIVATED,
        #   date_joined in the activation window is not expired.
        self.assertEqual(0, len(RegistrationProfile.objects.expired()))

        # * User with is_active=False, activation_key != ACTIVATED,
        #   date_joined too old to be in activation window is expired.
        User.objects.filter(username=user.username).update(
            date_joined=models.F('date_joined') - datetime.timedelta(
                settings.ACCOUNT_ACTIVATION_DAYS + 1
            )
        )
        self.assertEqual(1, len(RegistrationProfile.objects.expired()))
        self.assertEqual(
            [user.username],
            list(RegistrationProfile.objects.expired().values_list(
                'user__username', flat=True
            ))
        )

        # * User with is_active=True, activation_key=ACTIVATED,
        #   date_joined too old to be in activation window is not
        #   expired.
        user.is_active = True
        user.save()
        self.assertEqual(0, len(RegistrationProfile.objects.expired()))

        # * User with is_active=True, activation_key != ACTIVATED,
        #   date_joined too old to be in activation window is not
        #   expired.
        profile.activation_key = original_activation_key
        profile.save()
        self.assertEqual(0, len(RegistrationProfile.objects.expired()))

        # * User with is_active=True, activation_key != ACTIVATED,
        #   date_joined in the activation window is not expired.
        user.date_joined = original_date_joined
        user.save()
        self.assertEqual(0, len(RegistrationProfile.objects.expired()))

    @override_settings(USE_TZ=True)
    def test_expired_query_tz(self):
        """
        The expired() method still functions with time zones enabled.

        """
        self.test_expired_query()
