import datetime
import hashlib

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.core import management
from django.test import TestCase
from django.utils.six import text_type

from ..models import RegistrationProfile, SHA1_RE


class RegistrationModelTests(TestCase):
    """
    Test the model and manager used in the default backend.

    """
    user_info = {'username': 'alice',
                 'password': 'swordfish',
                 'email': 'alice@example.com'}

    def setUp(self):
        self.old_activation = getattr(
            settings, 'ACCOUNT_ACTIVATION_DAYS', None
        )
        settings.ACCOUNT_ACTIVATION_DAYS = 7

    def tearDown(self):
        settings.ACCOUNT_ACTIVATION_DAYS = self.old_activation

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
        self.assertEqual(text_type(profile),
                         "Registration information for alice")

    def test_activation_email(self):
        """
        ``RegistrationProfile.send_activation_email`` sends an
        email.

        """
        new_user = User.objects.create_user(**self.user_info)
        profile = RegistrationProfile.objects.create_profile(new_user)
        profile.send_activation_email(Site.objects.get_current())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user_info['email']])

    def test_user_creation(self):
        """
        Creating a new user populates the correct data, and sets the
        user's account inactive.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            **self.user_info
        )
        self.assertEqual(new_user.username, 'alice')
        self.assertEqual(new_user.email, 'alice@example.com')
        self.assertTrue(new_user.check_password('swordfish'))
        self.assertFalse(new_user.is_active)

    def test_user_creation_email(self):
        """
        By default, creating a new user sends an activation email.

        """
        RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            **self.user_info
        )
        self.assertEqual(len(mail.outbox), 1)

    def test_user_creation_no_email(self):
        """
        Passing ``send_email=False`` when creating a new user will not
        send an activation email.

        """
        RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            send_email=False,
            **self.user_info
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_unexpired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``False``
        within the activation window.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            **self.user_info
        )
        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertFalse(profile.activation_key_expired())

    def test_expired_account(self):
        """
        ``RegistrationProfile.activation_key_expired()`` is ``True``
        outside the activation window.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            **self.user_info
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
            site=Site.objects.get_current(),
            **self.user_info
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
        Attempting to activate outside the permitted window does not
        activate the account.

        """
        new_user = RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            **self.user_info
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

        new_user = User.objects.get(username='alice')
        self.assertFalse(new_user.is_active)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertNotEqual(
            profile.activation_key, RegistrationProfile.ACTIVATED
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
            site=Site.objects.get_current(),
            **self.user_info
        )
        profile = RegistrationProfile.objects.get(user=new_user)
        RegistrationProfile.objects.activate_user(profile.activation_key)

        profile = RegistrationProfile.objects.get(user=new_user)
        self.assertFalse(
            RegistrationProfile.objects.activate_user(
                profile.activation_key))

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
                invalid_key))

    def test_expired_user_deletion(self):
        """
        ``RegistrationProfile.objects.delete_expired_users()`` only
        deletes inactive users whose activation window has expired.

        """
        RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            **self.user_info
        )
        expired_user = RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            username='bob',
            password='secret',
            email='bob@example.com'
        )
        expired_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1
        )
        expired_user.save()

        RegistrationProfile.objects.delete_expired_users()
        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertRaises(User.DoesNotExist, User.objects.get, username='bob')

    def test_management_command(self):
        """
        The ``cleanupregistration`` management command properly
        deletes expired accounts.

        """
        RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            **self.user_info
        )
        expired_user = RegistrationProfile.objects.create_inactive_user(
            site=Site.objects.get_current(),
            username='bob',
            password='secret',
            email='bob@example.com'
        )
        expired_user.date_joined -= datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS + 1
        )
        expired_user.save()

        management.call_command('cleanupregistration')
        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertRaises(User.DoesNotExist, User.objects.get, username='bob')
