# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def load_repos( app, schema_editor ):
  Repo = app.get_model( 'Repos', 'Repo' )

  release_list = ( ( 'dev', [ 'dev', 'stage', 'prod' ] ), ( 'stage', [ 'stage', 'prod' ] ), ( 'prod', [ 'prod' ] ) )

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='APT - {0}'.format( release.title() ), manager_type='apt', name='apt-{0}'.format( release ), filesystem_dir='apt-{0}'.format( release ) )
    r.distroversion_list = [ 'precise', 'trusty', 'xenial' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='YUM - {0}'.format( release.title() ), manager_type='yum', name='yum-{0}'.format( release ), filesystem_dir='yum-{0}'.format( release ) )
    r.distroversion_list = [ 'centos6', 'centos7', 'sles11', 'sles12' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='JSON - {0}'.format( release.title() ), manager_type='json', name='json-{0}'.format( release ), filesystem_dir='json-{0}'.format( release ), show_only_latest=False )
    r.distroversion_list = [ 'resource' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='Docker - {0}'.format( release.title() ), manager_type='docker', name='docker-{0}'.format( release ), filesystem_dir='docker-{0}'.format( release ), show_only_latest=False )
    r.distroversion_list = [ 'docker' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()

  for release, release_type_list in release_list:
    r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', description='PYPI - {0}'.format( release.title() ), manager_type='pypi', name='pypi-{0}'.format( release ), filesystem_dir='pypi-{0}'.format( release ), show_only_latest=False )
    r.distroversion_list = [ 'pypi' ]
    r.release_type_list = release_type_list
    r.full_clean()
    r.save()


def load_distro_versions( app, schema_editor ):
  DistroVersion = app.get_model( 'Repos', 'DistroVersion' )

  for version in ( 'precise', 'trusty', 'xenial' ):
    d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=version, file_type='deb', version=version, release_names=version, distro='debian' )
    d.full_clean()
    d.save()

  for version, release_name, name in ( ( 'el6', '6', 'centos6' ), ( 'el7', '7', 'centos7' ) ):
    d = DistroVersion( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=name, file_type='rpm', version=version, release_names=release_name, distro='centos' )
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


def load_release_types( app, schema_editor ):
  ReleaseType = app.get_model( 'Repos', 'ReleaseType' )

  type_list = ( ( 'new', 'New', 1 ), ( 'dev', 'Development', 20 ), ( 'stage', 'Staging', 40 ), ( 'prod', 'Production', 60 ), ( 'depr', 'Deprocated', 100 ) )

  for name, description, level in type_list:
    r = ReleaseType( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name=name, level=level, change_control_required=( name == 'prod' ), description=description )
    r.full_clean()
    r.save()


def load_mirrors( app, schema_editor ):
  Mirror = app.get_model( 'Repos', 'Mirror' )

  m = Mirror( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='prod', description='Production', psk='prod' )
  repo_list = []
  for release in ( 'prod', ):
    repo_list += [ 'apt-{0}'.format( release ), 'yum-{0}'.format( release ), 'json-{0}'.format( release ), 'docker-{0}'.format( release ), 'pypi-{0}'.format( release ) ]
  m.repo_list = repo_list
  m.full_clean()
  m.save()

  m = Mirror( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='stage', description='Staging', psk='stage' )
  repo_list = []
  for release in ( 'stage', ):
    repo_list += [ 'apt-{0}'.format( release ), 'yum-{0}'.format( release ), 'json-{0}'.format( release ), 'docker-{0}'.format( release ), 'pypi-{0}'.format( release ) ]
  m.repo_list = repo_list
  m.full_clean()
  m.save()

  m = Mirror( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', name='dev', description='Developent', psk='dev' )
  repo_list = []
  for release in ( 'dev', ):
    repo_list += [ 'apt-{0}'.format( release ), 'yum-{0}'.format( release ), 'json-{0}'.format( release ), 'docker-{0}'.format( release ), 'pypi-{0}'.format( release ) ]
  m.repo_list = repo_list
  m.full_clean()
  m.save()


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
                ('deprocated_count', models.IntegerField( default=10 )),
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
                ('level', models.IntegerField(unique=True)),
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
                ('show_only_latest', models.BooleanField(default=True)),
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
        migrations.RunPython( load_release_types ),
        migrations.RunPython( load_mirrors ),
    ]
