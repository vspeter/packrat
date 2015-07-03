# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Repos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distroversion',
            name='distro',
            field=models.CharField(max_length=6, choices=[(b'debian', b'Debian'), (b'centos', b'Centos'), (b'rhel', b'RHEL'), (b'sles', b'SLES'), (b'core', b'CoreOS'), (b'none', b'None')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='distroversion',
            name='file_type',
            field=models.CharField(max_length=3, choices=[(b'deb', b'deb'), (b'rpm', b'RPM'), (b'rsc', b'Resource')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='packagefile',
            name='type',
            field=models.CharField(max_length=3, editable=False, choices=[(b'deb', b'deb'), (b'rpm', b'RPM'), (b'rsc', b'Resource')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='repo',
            name='manager_type',
            field=models.CharField(max_length=6, choices=[(b'apt', b'APT'), (b'yum', b'YUM'), (b'zypper', b'Zypper'), (b'json', b'JSON')]),
            preserve_default=True,
        ),
    ]
