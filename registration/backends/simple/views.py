from django.contrib.auth import authenticate, get_user_model, login

from registration import signals
from registration.views import RegistrationView as BaseRegistrationView


User = get_user_model()


class RegistrationView(BaseRegistrationView):
    """
    Registration via the simplest possible workflow: a user supplies a
    username, email address and password (the bare minimum for a
    useful account), and is immediately signed up and logged in).

    """
    def register(self, **cleaned_data):
        username, email, password = (cleaned_data['username'],
                                     cleaned_data['email'],
                                     cleaned_data['password1'])
        User.objects.create_user(username, email, password)

        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=self.request)
        return new_user

    def get_success_url(self, user):
        return '/'
