# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='uweet',
            name='date_posted',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 18, 8, 43, 40, 460551, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
