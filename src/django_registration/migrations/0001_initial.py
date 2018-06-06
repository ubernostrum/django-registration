# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


# django-registration 2.x included a model-based signup workflow which
# needed to create a model to store data. In django-registration 3.x,
# that workflow no longer exists.
#
# To avoid breaking existing sites with migrations which had
# dependencies on that migration, and ensure they can safely reverse
# and replay migrations, this migration is preserved, but is now a
# no-op.


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(
            migrations.RunPython.noop,
            migrations.RunPython.noop
        )
    ]
