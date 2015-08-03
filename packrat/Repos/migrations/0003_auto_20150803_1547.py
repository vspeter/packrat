# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Repos', '0002_auto_20150703_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repo',
            name='manager_type',
            field=models.CharField(max_length=6, choices=[(b'apt', b'APT'), (b'yum', b'YUM'), (b'yast', b'YaST'), (b'json', b'JSON')]),
            preserve_default=True,
        ),
    ]
