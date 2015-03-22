# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


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
                ('file_type', models.CharField(max_length=3, choices=[(b'deb', b'deb'), (b'rpm', b'rpm')])),
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
                ('type', models.CharField(max_length=3, editable=False, choices=[(b'deb', b'deb'), (b'rpm', b'rpm')])),
                ('arch', models.CharField(max_length=6, editable=False, choices=[(b'x86_64', b'x86_64'), (b'i386', b'i386'), (b'all', b'All')])),
                ('justification', models.TextField()),
                ('provenance', models.TextField()),
                ('file', models.FileField(upload_to=b'')),
                ('prod_changecontrol_id', models.CharField(max_length=20)),
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
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('manager_type', models.CharField(max_length=6, choices=[(b'apt', b'apt'), (b'yum', b'yum'), (b'zypper', b'zypper')])),
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
    ]
