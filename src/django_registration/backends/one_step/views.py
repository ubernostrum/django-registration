"""
A one-step (user signs up and is immediately active and logged in)
workflow.

"""

from django.contrib.auth import authenticate, get_user_model, login
from django.urls import reverse_lazy

from django_registration import signals
from django_registration.views import RegistrationView as BaseRegistrationView


User = get_user_model()


class RegistrationView(BaseRegistrationView):
    """
    Registration via the simplest possible process: a user supplies a
    username, email address and password (the bare minimum for a
    useful account), and is immediately signed up and logged in.

    """
    success_url = reverse_lazy('django_registration_complete')

    def register(self, form):
        new_user = form.save()
        new_user = authenticate(**{
            User.USERNAME_FIELD: new_user.get_username(),
            'password': form.cleaned_data['password1']
        })
        login(self.request, new_user)
        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=self.request
        )
        return new_user
