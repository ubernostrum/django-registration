"""
A management command which deletes used regiatration profiles (e.g.
the registration code for users that have allready activated) from the database.

Calls ``RegistrationProfile.objects.delete_activated_profiles()``, which
contains the actual logic for determining which accounts are deleted.

"""

from django.core.management.base import BaseCommand

from registration.models import RegistrationProfile


class Command(BaseCommand):
    help = "Delete used registration codes from the database"

    def handle(self, **options):
        RegistrationProfile.objects.delete_activated_profiles()
