"""
A two-step (registration followed by activation) workflow, implemented by emailing
an HMAC-verified timestamped activation token to the user on signup.

"""

# SPDX-License-Identifier: BSD-3-Clause

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django_registration import signals
from django_registration.exceptions import ActivationError
from django_registration.views import ActivationView as BaseActivationView
from django_registration.views import RegistrationView as BaseRegistrationView

from . import REGISTRATION_SALT
from .forms import ActivationForm

# pylint: disable=raise-missing-from


class RegistrationView(BaseRegistrationView):
    """
    A subclass of :class:`django_registration.views.RegistrationView` implementing
    the signup portion of this workflow.

    Important customization points unique to this class are:

    .. automethod:: create_inactive_user

    .. automethod:: get_activation_key

    .. automethod:: get_email_context

    .. attribute:: email_body_template

       A string specifying the template to use for the body of the activation
       email. Default is ``"django_registration/activation_email_body.txt"``.

    .. attribute:: email_subject_template

       A string specifying the template to use for the subject of the activation
       email. Default is ``"django_registration/activation_email_subject.txt"``. Note
       that, to avoid `header-injection vulnerabilities
       <https://en.wikipedia.org/wiki/Email_injection>`_, the result of rendering this
       template will be forced into a single line of text, stripping newline characters.

    """

    email_body_template = "django_registration/activation_email_body.txt"
    email_subject_template = "django_registration/activation_email_subject.txt"
    success_url = reverse_lazy("django_registration_complete")

    def register(self, form):
        """
        Register the new user account.

        """
        new_user = self.create_inactive_user(form)
        signals.user_registered.send(
            sender=self.__class__, user=new_user, request=self.request
        )
        return new_user

    def create_inactive_user(self, form):
        """
        Creates and returns an inactive user account, and calls
        :meth:`send_activation_email()` to send the email with the activation key. The
        argument ``form`` is a valid registration form instance passed from
        :meth:`~django_registration.views.RegistrationView.register()`.

        :param django_registration.forms.RegistrationForm form: The registration form.
        :rtype: django.contrib.auth.models.AbstractUser

        """
        new_user = form.save(commit=False)
        new_user.is_active = False
        new_user.save()

        self.send_activation_email(new_user)

        return new_user

    def get_activation_key(self, user):
        """
        Generates and returns the activation key which will be emailed to the user.

        :param django.contrib.auth.models.AbstractUser user: The new user account.
        :rtype: str

        """
        return signing.dumps(obj=user.get_username(), salt=REGISTRATION_SALT)

    def get_email_context(self, activation_key):
        """
        Returns a dictionary of values to be used as template context when generating the
        activation email.

        :param str activation_key: The activation key for the new user account.
        :rtype: dict

        """
        scheme = "https" if self.request.is_secure() else "http"
        return {
            "scheme": scheme,
            "activation_key": activation_key,
            "expiration_days": settings.ACCOUNT_ACTIVATION_DAYS,
            "site": get_current_site(self.request),
        }

    def send_activation_email(self, user):
        """
        Given an inactive user account, generates and sends the activation email for that
        account.

        :param django.contrib.auth.models.AbstractUser user: The new user account.
        :rtype: None

        """
        activation_key = self.get_activation_key(user)
        context = self.get_email_context(activation_key)
        context["user"] = user
        subject = render_to_string(
            template_name=self.email_subject_template,
            context=context,
            request=self.request,
        )
        # Force subject to a single line to avoid header-injection issues.
        subject = "".join(subject.splitlines())
        message = render_to_string(
            template_name=self.email_body_template,
            context=context,
            request=self.request,
        )
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)


class ActivationView(BaseActivationView):
    """
    A subclass of :class:`django_registration.views.ActivationView` implementing the
    activation portion of this workflow.

    This view expects to receive the activation key as the querystring parameter
    ``activation_key`` on the initial HTTP ``GET``; then it will populate that into an
    :class:`~django_registration.backends.activation.forms.ActivationForm` for
    re-submission in an HTTP ``POST`` request.

    If the activation key is missing, expired, or has an invalid signature, the form
    will have an error on the ``activation_key`` field.

    If the activation key has a valid non-expired signature, but account activation
    fails for another reason, the ``activation_error`` dictionary in the template
    context will contain a ``code`` key with one of the following values:

    ``"already_activated"``
       Indicates the account has already been activated.

    ``"bad_username"``
       Indicates the username decoded from the activation key is invalid (does not
       correspond to any user account).

    """

    ALREADY_ACTIVATED_MESSAGE = _(
        "The account you tried to activate has already been activated."
    )
    BAD_USERNAME_MESSAGE = _("The account you attempted to activate is invalid.")

    form_class = ActivationForm
    success_url = reverse_lazy("django_registration_activation_complete")

    def get_activation_data(self, request):
        """
        Return the activation key as initial form data.

        """
        activation_key = request.GET.get("activation_key")
        if activation_key is not None:
            return {"activation_key": activation_key}
        return {}

    def activate(self, form):
        """
        Attempt to activate the user account.

        """
        username = form.cleaned_data["activation_key"]
        user = self.get_user(username)
        user.is_active = True
        user.save()
        return user

    def get_user(self, username):
        """
        Given the verified username, look up and return the corresponding user
        account if it exists, or raising ``ActivationError`` if it doesn't.

        """
        # pylint: disable=invalid-name
        User = get_user_model()
        try:
            user = User.objects.get(**{User.USERNAME_FIELD: username})
            if user.is_active:
                raise ActivationError(
                    self.ALREADY_ACTIVATED_MESSAGE, code="already_activated"
                )
            return user
        except User.DoesNotExist:
            raise ActivationError(self.BAD_USERNAME_MESSAGE, code="bad_username")
