# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def migrate_repo_setdirectory( apps, schema_editor ):
  for repo in apps.get_model( 'Repos', 'Repo' ).objects.all():
    repo.filesystem_dir = repo.name.replace( '-', '/' )
    repo.save()

class Migration(migrations.Migration):

    dependencies = [
        ('Repos', '0004_auto_20160510_0503'),
    ]

    operations = [
        migrations.AddField(
            model_name='repo',
            name='filesystem_dir',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.RunPython( migrate_repo_setdirectory ),
    ]
