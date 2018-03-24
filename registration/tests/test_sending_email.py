from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings

from ..backends.hmac.views import RegistrationView, ActivationView

User = get_user_model()


@override_settings(
    ACCOUNT_ACTIVATION_DAYS=7,
    REGISTRATION_OPEN=True
)
class SendActivationEmailTestCase(TestCase):
    """
    Check if we send correct context in activation email.
    Check if activation_key passed to email template can be
    actually verified.
    Subject template should contain only {{activation key}}.
    Body template should contain {{scheme}}, {{expiration_days}}, {{site}}.
    """
    user_model = User

    valid_data = {
        User.USERNAME_FIELD: 'alice',
        'email': 'alice@example.com',
        'password': 'swordfish',
    }

    def setUp(self):
        # clear the outbox
        mail.outbox = []
        # create inactive user
        self.user = self.user_model.objects.create_user(**self.valid_data)
        self.user.is_active = False
        self.user.save()
        # create sample request
        self.request = RequestFactory()
        self.request.is_secure = False

    def test_send_activation_email(self):
        """
        Make sure that e-mail body and subject contains our context.
        Verify user based on activation_key sent in email subject.
        """
        # send activation email to user
        RegistrationView(request=self.request).send_activation_email(self.user)
        # grab that email and verify that it contains desired data
        email = mail.outbox[0]
        # BODY
        # scheme
        self.assertIn('http', email.body)
        # site
        self.assertIn('example.com', email.body)
        # expiration days
        self.assertIn('7', email.body)
        # user
        self.assertIn(self.valid_data[User.USERNAME_FIELD], email.body)
        # check if user is inactive
        self.user.refresh_from_db()
        self.assertIs(False, self.user.is_active)
        # grab activation key from email subject and activate user
        activation_key = email.subject
        user = ActivationView().activate(activation_key=activation_key)
        # make sure that's correct user
        self.user.refresh_from_db()
        self.assertEqual(self.user, user)
        # make sure hes active
        self.assertIs(True, self.user.is_active)

    @override_settings(DEFAULT_FROM_EMAIL='from@example.com')
    def test_send_activation_email_from_settings(self):
        """
        Check if function is picking up settings.
        """
        # send email to user
        RegistrationView(request=self.request).send_activation_email(self.user)
        # grab email from outbox
        email = mail.outbox[0]
        # verify from_email
        self.assertEqual(email.from_email, 'from@example.com')

    @override_settings(DEFAULT_FROM_EMAIL='from@example.com')
    def test_send_activation_email_kwargs(self):
        """
        Test if additional kwargs are passed to function
        and settings are overwritten.
        """
        kwargs = {
            'from_email': 'test@o2.pl',
        }
        # send email to user
        RegistrationView(request=self.request)\
            .send_activation_email(self.user, **kwargs)
        # grab email from outbox
        email = mail.outbox[0]
        # verify from_email
        self.assertEqual(email.from_email, kwargs['from_email'])
