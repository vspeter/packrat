# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def load_repos( app, schema_editor ):
  Repo = app.get_model( 'Repos', 'Repo' )

  release_list = ( 'dev', 'stage', 'prod' )

  for release in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='APT - {0}'.format( release.title() ), manager_type='apt', name='apt-{0}'.format( release ), filesystem_dir='apt-{0}'.format( release ) )
    r.distroversion_list = [ 'precise', 'trusty', 'xenial' ]
    r.full_clean()
    r.save()

  for release in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='YUM - {0}'.format( release.title() ), manager_type='yum', name='yum-{0}'.format( release ), filesystem_dir='yum-{0}'.format( release ) )
    r.distroversion_list = [ 'centos6', 'centos7', 'sles11', 'sles12' ]
    r.full_clean()
    r.save()

  for release in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='JSON - {0}'.format( release.title() ), manager_type='json', name='json-{0}'.format( release ), filesystem_dir='json-{0}'.format( release ) )
    r.distroversion_list = [ 'resource' ]
    r.full_clean()
    r.save()

  for release in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='Docker - {0}'.format( release.title() ), manager_type='docker', name='docker-{0}'.format( release ), filesystem_dir='docker-{0}'.format( release ) )
    r.distroversion_list = [ 'docker' ]
    r.full_clean()
    r.save()

  for release in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='PYPI  - {0}'.format( release.title() ), manager_type='pypi', name='pypi-{0}'.format( release ), filesystem_dir='pypi-{0}'.format( release ) )
    r.distroversion_list = [ 'python' ]
    r.full_clean()
    r.save()


def load_distro_versions( app, schema_editor ):
  DistroVersion = app.get_model( 'Repos', 'DistroVersion' )

  for version in ( 'precise', 'trusty', 'xenial' ):
    d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=version, file_type='deb', version=version, release_names=version, distro='debian' )
    d.full_clean()
    d.save()

  for version, name in ( ( 'el6', '6' ), ( 'el7', '7' ) ):
    d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=version, file_type='rpm', version=version, release_names=name, distro='centos' )
    d.full_clean()
    d.save()

  for version, name in ( ( 'sles11', '11' ), ( 'sles12', '12' ) ):
    d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=version, file_type='rpm', version=version, release_names=name, distro='sles' )
    d.full_clean()
    d.save()

  d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='resource', file_type='rsc', distro='none' )
  d.full_clean()
  d.save()

  d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='docker', file_type='docker', distro='none' )
  d.full_clean()
  d.save()

  d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='pypi', file_type='python', distro='none' )
  d.full_clean()
  d.save()


def create_release_types( app, schema_editor ):
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


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DistroVersion',
            fields=[
                ('name', models.CharField(serialize=False, max_length=20, primary_key=True)),
                ('distro', models.CharField(choices=[('debian', 'Debian'), ('centos', 'Centos'), ('rhel', 'RHEL'), ('sles', 'SLES'), ('core', 'CoreOS'), ('none', 'None')], max_length=6)),
                ('version', models.CharField(blank=True, null=True, max_length=10)),
                ('file_type', models.CharField(choices=[('deb', 'deb'), ('rpm', 'RPM'), ('rsc', 'Resource'), ('docker', 'Docker'), ('python', 'Python')], max_length=6)),
                ('release_names', models.CharField(blank=True, help_text='tab delimited list of things like el5, trusty, something that is in filename that tells what version it belongs to', max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Mirror',
            fields=[
                ('name', models.CharField(serialize=False, max_length=50, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('psk', models.CharField(max_length=100)),
                ('last_heartbeat', models.DateTimeField(blank=True, null=True, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('name', models.CharField(serialize=False, max_length=200, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PackageFile',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('version', models.CharField(max_length=50, editable=False)),
                ('type', models.CharField(choices=[('deb', 'deb'), ('rpm', 'RPM'), ('rsc', 'Resource'), ('docker', 'Docker'), ('python', 'Python')], max_length=6, editable=False)),
                ('arch', models.CharField(choices=[('x86_64', 'x86_64'), ('i386', 'i386'), ('all', 'All')], max_length=6, editable=False)),
                ('justification', models.TextField()),
                ('provenance', models.TextField()),
                ('file', models.FileField(upload_to='', editable=False)),
                ('sha256', models.CharField(max_length=64, editable=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('distroversion', models.ForeignKey(to='Repos.DistroVersion', editable=False)),
                ('package', models.ForeignKey(to='Repos.Package', editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='PackageFileReleaseType',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('at', models.DateTimeField(auto_now_add=True)),
                ('change_control_id', models.CharField(blank=True, null=True, max_length=50)),
                ('package_file', models.ForeignKey(to='Repos.PackageFile')),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseType',
            fields=[
                ('name', models.CharField(serialize=False, max_length=10, primary_key=True)),
                ('description', models.CharField(max_length=100)),
                ('level', models.IntegerField()),
                ('change_control_required', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('name', models.CharField(serialize=False, max_length=50, primary_key=True)),
                ('filesystem_dir', models.CharField(unique=True, max_length=50)),
                ('manager_type', models.CharField(choices=[('apt', 'APT'), ('yum', 'YUM'), ('yast', 'YaST'), ('json', 'JSON'), ('docker', 'Docker'), ('pypi', 'PyPi')], max_length=6)),
                ('description', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('distroversion_list', models.ManyToManyField(to='Repos.DistroVersion')),
                ('release_type_list', models.ManyToManyField(to='Repos.ReleaseType')),
            ],
        ),
        migrations.AddField(
            model_name='packagefilereleasetype',
            name='release_type',
            field=models.ForeignKey(to='Repos.ReleaseType'),
        ),
        migrations.AddField(
            model_name='packagefile',
            name='release_type',
            field=models.ManyToManyField(through='Repos.PackageFileReleaseType', to='Repos.ReleaseType'),
        ),
        migrations.AddField(
            model_name='mirror',
            name='repo_list',
            field=models.ManyToManyField(to='Repos.Repo'),
        ),
        migrations.AlterUniqueTogether(
            name='distroversion',
            unique_together=set([('distro', 'version', 'file_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='packagefilereleasetype',
            unique_together=set([('package_file', 'release_type')]),
        ),
        migrations.AlterUniqueTogether(
            name='packagefile',
            unique_together=set([('package', 'distroversion', 'version', 'type', 'arch')]),
        ),
        migrations.RunPython( load_repos ),
        migrations.RunPython( load_distro_versions ),
        migrations.RunPython( create_release_types ),
    ]
