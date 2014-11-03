# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mirror', fields=[
                ('name', models.CharField(
                    max_length=50, serialize=False, primary_key=True)), ('description', models.CharField(
                        max_length=200)), ('psk', models.CharField(
                            max_length=100)), ('last_sync_start', models.DateTimeField(
                                null=True, editable=False, blank=True)), ('last_sync_complete', models.DateTimeField(
                                    null=True, editable=False, blank=True)), ('created', models.DateTimeField(
                                        auto_now_add=True)), ('updated', models.DateTimeField(
                                            auto_now=True)), ], options={}, bases=(
                models.Model,), ), migrations.CreateModel(
            name='Package', fields=[
                ('name', models.CharField(
                    max_length=200, serialize=False, primary_key=True)), ('created', models.DateTimeField(
                        auto_now_add=True)), ('updated', models.DateTimeField(
                            auto_now=True)), ], options={}, bases=(
                models.Model,), ), migrations.CreateModel(
            name='PackageFile', fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)), ('version', models.CharField(
                        max_length=50, editable=False)), ('type', models.CharField(
                            max_length=3, editable=False, choices=[
                                (b'deb', b'deb'), (b'rpm', b'rpm')])), ('arch', models.CharField(
                                    max_length=5, editable=False, choices=[
                                        (b'x86_64', b'x86_64'), (b'i386', b'i386'), (b'all', b'all')])), ('justification', models.TextField()), ('provenance', models.TextField()), ('file', models.FileField(
                                            upload_to=b'')), ('ci_at', models.DateTimeField(
                                                null=True, blank=True)), ('dev_at', models.DateTimeField(
                                                    null=True, blank=True)), ('stage_at', models.DateTimeField(
                                                        null=True, blank=True)), ('prod_at', models.DateTimeField(
                                                            null=True, blank=True)), ('created', models.DateTimeField(
                                                                auto_now_add=True)), ('updated', models.DateTimeField(
                                                                    auto_now=True)), ('package', models.ForeignKey(
                                                                        editable=False, to='repos.Package')), ], options={}, bases=(
                models.Model,), ), migrations.CreateModel(
            name='Repo', fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)), ('manager_type', models.CharField(
                        max_length=6, choices=[
                            (b'apt', b'apt'), (b'yum', b'yum'), (b'zypper', b'zypper')])), ('description', models.CharField(
                                max_length=200)), ('release_type', models.CharField(
                                    max_length=7, choices=[
                                        (b'ci', b'ci'), (b'dev', b'dev'), (b'stage', b'stage'), (b'prod', b'prod')])), ('created', models.DateTimeField(
                                            auto_now_add=True)), ('updated', models.DateTimeField(
                                                auto_now=True)), ], options={}, bases=(
                models.Model,), ), migrations.CreateModel(
            name='Version', fields=[
                ('id', models.AutoField(
                    verbose_name='ID', serialize=False, auto_created=True, primary_key=True)), ('distro', models.CharField(
                        max_length=6, choices=[
                            (b'debian', b'debian'), (b'centos', b'centos'), (b'rhel', b'rhel'), (b'sles', b'sles')])), ('version', models.CharField(
                                max_length=10)), ('release_names', models.CharField(
                                    max_length=100)), ('created', models.DateTimeField(
                                        auto_now_add=True)), ('updated', models.DateTimeField(
                                            auto_now=True)), ], options={}, bases=(
                models.Model,), ), migrations.AlterUniqueTogether(
            name='version', unique_together=set(
                [
                    ('distro', 'version')]), ), migrations.AddField(
            model_name='repo', name='version_list', field=models.ManyToManyField(
                to='repos.Version'), preserve_default=True, ), migrations.AlterUniqueTogether(
            name='packagefile', unique_together=set(
                [
                    ('package', 'version', 'type', 'arch')]), ), migrations.AddField(
            model_name='mirror', name='repo_list', field=models.ManyToManyField(
                to='repos.Repo'), preserve_default=True, ), ]
