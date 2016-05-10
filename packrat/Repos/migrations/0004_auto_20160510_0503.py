# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core import serializers

def migrate_repo_release_types( apps, schema_editor ):
  ReleaseType = apps.get_model( 'Repos', 'ReleaseType' )
  for repo in apps.get_model( 'Repos', 'Repo' ).objects.all():
    rt = ReleaseType.objects.get( name=repo.release_type )
    repo.release_type_list = [ rt ]
    repo.save()


def create_release_types( apps, schema_editor ):
  fixture = """
  [
  {
    "fields": {
      "description": "New",
      "level": 0,
      "change_control_required": false,
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z"
    },
    "model": "Repos.releasetype",
    "pk": "new"
  },
  {
    "fields": {
      "description": "CI",
      "level": 20,
      "change_control_required": false,
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z"
    },
    "model": "Repos.releasetype",
    "pk": "ci"
  },
  {
    "fields": {
      "description": "Development",
      "level": 40,
      "change_control_required": false,
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z"
    },
    "model": "Repos.releasetype",
    "pk": "dev"
  },
  {
    "fields": {
      "description": "Staging",
      "level": 60,
      "change_control_required": false,
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z"
    },
    "model": "Repos.releasetype",
    "pk": "stage"
  },
  {
    "fields": {
      "description": "Production",
      "level": 80,
      "change_control_required": true,
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z"
    },
    "model": "Repos.releasetype",
    "pk": "prod"
  },
  {
    "fields": {
      "description": "Deprocated",
      "level": 100,
      "change_control_required": false,
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z"
    },
    "model": "Repos.releasetype",
    "pk": "depr"
  }
  ]
  """
  objects = serializers.deserialize( 'json', fixture, ignorenonexistent=True)
  for obj in objects:
    obj.save()


def migrate_packagefile_release_types( apps, schema_editor ):
  PackageFileReleaseType = apps.get_model( 'Repos', 'PackageFileReleaseType' )
  for package_file in apps.get_model( 'Repos', 'PackageFile' ).objects.all():
    if package_file.depr_at:
      pfrt = PackageFileReleaseType()
      pfrt.package_file = package_file
      pfrt.release_type_id = 'depr'
      pfrt.at = package_file.depr_at
      pfrt.save()

    if package_file.prod_at:
      pfrt = PackageFileReleaseType()
      pfrt.package_file = package_file
      pfrt.release_type_id = 'prod'
      pfrt.at = package_file.prod_at
      pfrt.change_control_id = package_file.prod_changecontrol_id
      pfrt.save()

    if package_file.stage_at:
      pfrt = PackageFileReleaseType()
      pfrt.package_file = package_file
      pfrt.release_type_id = 'stage'
      pfrt.at = package_file.stage_at
      pfrt.save()

    if package_file.dev_at:
      pfrt = PackageFileReleaseType()
      pfrt.package_file = package_file
      pfrt.release_type_id = 'dev'
      pfrt.at = package_file.dev_at
      pfrt.save()

    if package_file.ci_at:
      pfrt = PackageFileReleaseType()
      pfrt.package_file = package_file
      pfrt.release_type_id = 'ci'
      pfrt.at = package_file.ci_at
      pfrt.save()


class Migration(migrations.Migration):

    dependencies = [
        ('Repos', '0003_auto_20150803_1547'),
    ]

    operations = [
        migrations.CreateModel(
            name='PackageFileReleaseType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('at', models.DateTimeField(auto_now_add=True)),
                ('change_control_id', models.CharField(max_length=50,blank=True,null=True)),
                ('package_file', models.ForeignKey(to='Repos.PackageFile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseType',
            fields=[
                ('name', models.CharField(max_length=10, serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=100)),
                ('level', models.IntegerField()),
                ('change_control_required', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='packagefilereleasetype',
            name='release_type',
            field=models.ForeignKey(to='Repos.ReleaseType'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='packagefilereleasetype',
            unique_together=set([('package_file', 'release_type')]),
        ),
        migrations.AddField(
            model_name='packagefile',
            name='release_type',
            field=models.ManyToManyField(to='Repos.ReleaseType', through='Repos.PackageFileReleaseType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='repo',
            name='release_type_list',
            field=models.ManyToManyField(to='Repos.ReleaseType'),
            preserve_default=True,
        ),
        migrations.RunPython( create_release_types ),
        migrations.RunPython( migrate_packagefile_release_types ),
        migrations.RemoveField(
            model_name='packagefile',
            name='ci_at',
        ),
        migrations.RemoveField(
            model_name='packagefile',
            name='depr_at',
        ),
        migrations.RemoveField(
            model_name='packagefile',
            name='dev_at',
        ),
        migrations.RemoveField(
            model_name='packagefile',
            name='prod_at',
        ),
        migrations.RemoveField(
            model_name='packagefile',
            name='prod_changecontrol_id',
        ),
        migrations.RemoveField(
            model_name='packagefile',
            name='stage_at',
        ),
        migrations.RunPython( migrate_repo_release_types ),
        migrations.RemoveField(
            model_name='repo',
            name='release_type',
        ),
        migrations.AlterField(
            model_name='distroversion',
            name='release_names',
            field=models.CharField(help_text=b'tab delimited list of things like el5, trusty, something that is in filename that tells what version it belongs to', max_length=100, blank=True),
            preserve_default=True,
        ),
    ]
