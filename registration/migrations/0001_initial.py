# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationProfile',
            fields=[
                ('id',
                 models.AutoField(
                     primary_key=True,
                     serialize=False,
                     auto_created=True,
                     verbose_name='ID')),
                ('activation_key',
                 models.CharField(
                     verbose_name='activation key',
                     max_length=40)),
                ('user',
                 models.OneToOneField(
                     to=settings.AUTH_USER_MODEL,
                     verbose_name='user',
                     on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'registration profile',
                'verbose_name_plural': 'registration profiles',
            },
        ),
    ]
