# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib

from django.db import models, migrations
from django.core import serializers

def migrate_repo_setname( apps, schema_editor ):
  for repo in apps.get_model( 'Repos', 'Repo' ).objects.all():
    repo.name = '%s-%s' % ( repo.manager_type, repo.release_type )
    repo.save()

def migrate_repo_release_types( apps, schema_editor ):
  ReleaseType = apps.get_model( 'Repos', 'ReleaseType' )
  for repo in apps.get_model( 'Repos', 'Repo' ).objects.all():
    rt = ReleaseType.objects.get( name=repo.release_type )
    repo.release_type_list = [ rt ]
    repo.name = '%s-%s' % ( repo.manager_type, repo.release_type )
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


def mirrors_save_repos( apps, schema_editor ):
  for mirror in apps.get_model( 'Repos', 'Mirror' ).objects.all():
    mirror.repo_ids = ','.join( [ str( i.id ) for i in mirror.repo_list.all() ] )
    mirror.save()
  for repo in apps.get_model( 'Repos', 'Repo' ).objects.all():
    repo.distro_ids = ','.join( [ str( i.pk ) for i in repo.distroversion_list.all() ] )
    repo.save()

def mirrors_restore_repos( apps, schema_editor ):
  Repo = apps.get_model( 'Repos', 'Repo' )
  DistroVersion = apps.get_model( 'Repos', 'DistroVersion' )
  for mirror in apps.get_model( 'Repos', 'Mirror' ).objects.all():
    id_list = [ int( i ) for i in mirror.repo_ids.split( ',' ) ]
    mirror.repo_list = [ Repo.objects.get( id=id ) for id in id_list ]
    mirror.save()

  for repo in apps.get_model( 'Repos', 'Repo' ).objects.all():
    id_list = [ i for i in repo.distro_ids.split( ',' ) ]
    repo.distroversion_list = [ DistroVersion.objects.get( pk=id ) for id in id_list ]
    repo.save()

def packagefile_loadsha256( apps, schema_editor ):
  for pf in apps.get_model( 'Repos', 'PackageFile' ).objects.all():
    sha256 = hashlib.sha256()
    wrk = open( pf.file.path, 'r' )
    buff = wrk.read( 4096 )
    while buff:
      sha256.update( buff )
      buff = wrk.read( 4096 )
    pf.sha256 = sha256.hexdigest()
    pf.save()

class Migration(migrations.Migration):

    dependencies = [
        ('Repos', '0003_auto_20150803_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='repo',
            name='name',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.RunPython( migrate_repo_setname ),

        migrations.AddField(
            model_name='mirror',
            name='repo_ids',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='repo',
            name='distro_ids',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.RunPython( mirrors_save_repos ),
        migrations.RemoveField(
            model_name='mirror',
            name='repo_list',
        ),
        migrations.RemoveField(
            model_name='repo',
            name='distroversion_list',
        ),
        migrations.AlterField(
            model_name='repo',
            name='id',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='repo',
            name='name',
            field=models.CharField(max_length=50, serialize=False, primary_key=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mirror',
            name='repo_list',
            field=models.ManyToManyField(to='Repos.Repo'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='repo',
            name='distroversion_list',
            field=models.ManyToManyField(to='Repos.DistroVersion'),
            preserve_default=True,
        ),
        migrations.RunPython( mirrors_restore_repos ),
        migrations.RemoveField(
            model_name='repo',
            name='id',
        ),
        migrations.RemoveField(
            model_name='mirror',
            name='repo_ids',
        ),
        migrations.RemoveField(
            model_name='repo',
            name='distro_ids',
        ),

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
        migrations.RemoveField(
            model_name='mirror',
            name='last_sync_complete',
        ),
        migrations.RemoveField(
            model_name='mirror',
            name='last_sync_start',
        ),
        migrations.AddField(
            model_name='mirror',
            name='last_heartbeat',
            field=models.DateTimeField(null=True, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='packagefile',
            name='sha256',
            field=models.CharField(default='', max_length=64, editable=False),
            preserve_default=False,
        ),
        migrations.RunPython( packagefile_loadsha256 ),
    ]
