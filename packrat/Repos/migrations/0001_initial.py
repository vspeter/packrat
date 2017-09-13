# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core import serializers

def load_repos( apps, schema_editor ):
  Repo = apps.get_model( "Repos", "Repo" )
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=1, manager_type='apt', release_type='ci', description='APT - CI' )
  r.distroversion_list = [ 'precise', 'trusty', 'xenial' ]
  r.save()
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=2, manager_type='apt', release_type='dev', description='APT - Dev' )
  r.distroversion_list = [ 'precise', 'trusty', 'xenial' ]
  r.save()
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=3, manager_type='apt', release_type='stage', description='APT - Stage' )
  r.distroversion_list = [ 'precise', 'trusty', 'xenial' ]
  r.save()
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=4, manager_type='apt', release_type='prod', description='APT - Prod' )
  r.distroversion_list = [ 'precise', 'trusty', 'xenial' ]
  r.save()

  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=8, manager_type='yum', release_type='ci', description='YUM - CI' )
  r.distroversion_list = [ 'centos6', 'centos7', 'sles11', 'sles12' ]
  r.save()
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=7, manager_type='yum', release_type='dev', description='YUM - Dev' )
  r.distroversion_list = [ 'centos6', 'centos7', 'sles11', 'sles12' ]
  r.save()
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=6, manager_type='yum', release_type='stage', description='YUM - Stage' )
  r.distroversion_list = [ 'centos6', 'centos7', 'sles11', 'sles12' ]
  r.save()
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=5, manager_type='yum', release_type='prod', description='YUM - Prod' )
  r.distroversion_list = [ 'centos6', 'centos7', 'sles11', 'sles12' ]
  r.save()

  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=9, manager_type='json', release_type='ci', description='JSON - CI' )
  r.distroversion_list = [ 'resource' ]
  r.save()
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=10, manager_type='json', release_type='dev', description='JSON - Dev' )
  r.distroversion_list = [ 'resource' ]
  r.save()
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=11, manager_type='json', release_type='stage', description='JSON - Stage' )
  r.distroversion_list = [ 'resource' ]
  r.save()
  r = Repo( updated='2010-01-01T00:00:00.000Z', created='2010-01-01T00:00:00.000Z', pk=12, manager_type='json', release_type='prod', description='JSON - Prod' )
  r.distroversion_list = [ 'resource' ]
  r.save()



def load_distro_versions( apps, schema_editor ):
  fixture = """
[
  {
    "fields": {
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z",
      "file_type": "deb",
      "version": "precise",
      "release_names": "precise",
      "distro": "debian"
    },
    "model": "Repos.distroversion",
    "pk": "precise"
  },
  {
    "fields": {
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z",
      "file_type": "deb",
      "version": "trusty",
      "release_names": "trusty",
      "distro": "debian"
    },
    "model": "Repos.distroversion",
    "pk": "trusty"
  },
  {
    "fields": {
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z",
      "file_type": "deb",
      "version": "xenial",
      "release_names": "xenial",
      "distro": "debian"
    },
    "model": "Repos.distroversion",
    "pk": "xenial"
  },
  {
    "fields": {
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z",
      "file_type": "rpm",
      "version": "6",
      "release_names": "el6",
      "distro": "centos"
    },
    "model": "Repos.distroversion",
    "pk": "centos6"
  },
  {
    "fields": {
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z",
      "file_type": "rpm",
      "version": "7",
      "release_names": "el7",
      "distro": "centos"
    },
    "model": "Repos.distroversion",
    "pk": "centos7"
  },
  {
    "fields": {
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z",
      "file_type": "rpm",
      "version": "11",
      "release_names": "sles11",
      "distro": "sles"
    },
    "model": "Repos.distroversion",
    "pk": "sles11"
  },
  {
    "fields": {
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z",
      "file_type": "rpm",
      "version": "12",
      "release_names": "sles12",
      "distro": "sles"
    },
    "model": "Repos.distroversion",
    "pk": "sles12"
  },
  {
    "fields": {
      "updated": "2013-01-01T01:01:00Z",
      "created": "2013-01-01T01:01:00Z",
      "file_type": "rsc",
      "version": "",
      "release_names": "",
      "distro": "none"
    },
    "model": "Repos.distroversion",
    "pk": "resource"
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
                ('name', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('distro', models.CharField(max_length=6, choices=[(b'debian', b'Debian'), (b'centos', b'Centos'), (b'rhel', b'RHEL'), (b'sles', b'SLES')])),
                ('version', models.CharField(max_length=10)),
                ('file_type', models.CharField(max_length=3, choices=[(b'deb', b'deb'), (b'rpm', b'RPM'), (b'pdisk', b'Plato Disk')])),
                ('release_names', models.CharField(max_length=100, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Mirror',
            fields=[
                ('name', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('psk', models.CharField(max_length=100)),
                ('last_sync_start', models.DateTimeField(null=True, editable=False, blank=True)),
                ('last_sync_complete', models.DateTimeField(null=True, editable=False, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('name', models.CharField(max_length=200, serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PackageFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=50, editable=False)),
                ('type', models.CharField(max_length=3, editable=False, choices=[(b'deb', b'deb'), (b'rpm', b'RPM'), (b'pdisk', b'Plato Disk')])),
                ('arch', models.CharField(max_length=6, editable=False, choices=[(b'x86_64', b'x86_64'), (b'i386', b'i386'), (b'all', b'All')])),
                ('justification', models.TextField()),
                ('provenance', models.TextField()),
                ('file', models.FileField(upload_to=b'', editable=False)),
                ('prod_changecontrol_id', models.CharField(max_length=20, blank=True)),
                ('ci_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('dev_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('stage_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('prod_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('depr_at', models.DateTimeField(null=True, editable=False, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('distroversion', models.ForeignKey(editable=False, to='Repos.DistroVersion')),
                ('package', models.ForeignKey(editable=False, to='Repos.Package')),
            ],
            options={
                'default_permissions': ('change', 'promote', 'create'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('manager_type', models.CharField(max_length=6, choices=[(b'apt', b'APT'), (b'yum', b'YUM'), (b'zypper', b'Zypper')])),
                ('description', models.CharField(max_length=200)),
                ('release_type', models.CharField(max_length=5, choices=[(b'ci', b'CI'), (b'dev', b'Development'), (b'stage', b'Staging'), (b'prod', b'Production'), (b'depr', b'Deprocated')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('distroversion_list', models.ManyToManyField(to='Repos.DistroVersion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='packagefile',
            unique_together=set([('package', 'distroversion', 'version', 'type', 'arch')]),
        ),
        migrations.AddField(
            model_name='mirror',
            name='repo_list',
            field=models.ManyToManyField(to='Repos.Repo'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='distroversion',
            unique_together=set([('distro', 'version', 'file_type')]),
        ),
        migrations.RunPython( load_repos ),
        migrations.RunPython( load_distro_versions )
    ]
