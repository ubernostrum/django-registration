"""
A one-step (user signs up and is immediately active and logged in)
workflow.

"""
from django.contrib.auth import authenticate, get_user_model, login

from registration import signals
from registration.views import RegistrationView as BaseRegistrationView


User = get_user_model()


class RegistrationView(BaseRegistrationView):
    """
    Registration via the simplest possible process: a user supplies a
    username, email address and password (the bare minimum for a
    useful account), and is immediately signed up and logged in).

    """
    def register(self, **cleaned_data):
        user_kwargs = self.get_user_kwargs(**cleaned_data)
        User.objects.create_user(**user_kwargs)
        user_kwargs.pop('email')

        new_user = authenticate(**user_kwargs)
        login(self.request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def get_success_url(self, user):
        return '/'
