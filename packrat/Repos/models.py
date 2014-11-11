import os
import re
from django.core.exceptions import ValidationError
from django.db import models

MANAGER_TYPE_CHOICES = (
    ('apt', 'apt'), ('yum', 'yum'), ('zypper', 'zypper'))
FILE_TYPE_CHOICES = (('deb', 'deb'), ('rpm', 'rpm'))
FILE_ARCH_CHOICES = (
    ('x86_64', 'x86_64'), ('i386', 'i386'), ('all', 'all'))
RELEASE_TYPE_CHOICES = (
    ('ci', 'ci'), ('dev', 'dev'), ('stage', 'stage'), ('prod', 'prod'))
DISTRO_CHOICES = (('debian', 'debian'),
                  ('centos', 'centos'), ('rhel', 'rhel'), ('sles', 'sles'))
                  # there is no ubuntu, it shares the same version space as
                  # debian

MANAGER_TYPE_LENGTH = 6
FILE_TYPE_LENGTH = 3
FILE_ARCH_LENGTH = 6
RELEASE_TYPE_LENGTH = 5
DISTORY_LENGTH = 6


class DistroVersion(models.Model):
    # TODO: make the release_names another model
    name = models.CharField(max_length=20, primary_key=True)
    distro = models.CharField(
        max_length=DISTORY_LENGTH, choices=DISTRO_CHOICES)
        # TODO: convert into another model
    version = models.CharField(max_length=10)
    file_type = models.CharField(
        max_length=FILE_TYPE_LENGTH, choices=FILE_TYPE_CHOICES)
    release_names = models.CharField(max_length=100, blank=True)
        # '\t' delimited, things like el5, trusty,
        # something that is in filename that tells what version it belongs to
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    def __unicode__(self):
        return 'Version "%s" of "%s"' % (self.version, self.distro)

    class Meta:
        unique_together = ('distro', 'version', 'file_type')


class Repo(models.Model):
    distroversion_list = models.ManyToManyField(DistroVersion)
    manager_type = models.CharField(
        max_length=MANAGER_TYPE_LENGTH, choices=MANAGER_TYPE_CHOICES)
    description = models.CharField(max_length=200)
    release_type = models.CharField(
        max_length=RELEASE_TYPE_LENGTH, choices=RELEASE_TYPE_CHOICES)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    def __getattr__(self, name):
        if name == 'package_list':
            qs = Package.objects.filter(
                packagefile__distroversion__in=self.distroversion_list.all())

            if self.release_type == 'ci':
                qs = qs.filter(
                    packagefile__ci_at__isnull=False,
                    packagefile__dev_at__isnull=True,
                    packagefile__stage_at__isnull=True,
                    packagefile__prod_at__isnull=True).distinct()

            elif self.release_type == 'dev':
                qs = qs.filter(packagefile__dev_at__isnull=False,
                               packagefile__stage_at__isnull=True,
                               packagefile__prod_at__isnull=True).distinct()

            elif self.release_type == 'stage':
                qs = qs.filter(packagefile__stage_at__isnull=False,
                               packagefile__prod_at__isnull=True).distinct()

            elif self.release_type == 'prod':
                qs = qs.filter(packagefile__prod_at__isnull=False).distinct()

            return qs

        raise AttributeError(name)

    def __unicode__(self):
        return 'Repo "%s"' % self.description


class Mirror(models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    description = models.CharField(max_length=200)
    psk = models.CharField(max_length=100)
    repo_list = models.ManyToManyField(Repo)
    last_sync_start = models.DateTimeField(
        editable=False, blank=True, null=True)
    last_sync_complete = models.DateTimeField(
        editable=False, blank=True, null=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    def __unicode__(self):
        return 'Mirror "%s"' % self.description


class Package(models.Model):
    name = models.CharField(max_length=200, primary_key=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    def __unicode__(self):
        return 'Package "%s"' % self.name


class PackageFile(models.Model):
    package = models.ForeignKey(Package, editable=False)
    distroversion = models.ForeignKey(DistroVersion, editable=False)
    version = models.CharField(max_length=50, editable=False)
    type = models.CharField(
        max_length=FILE_TYPE_LENGTH, editable=False, choices=FILE_TYPE_CHOICES)
    arch = models.CharField(
        max_length=FILE_ARCH_LENGTH, editable=False, choices=FILE_ARCH_CHOICES)
    justification = models.TextField()
    provenance = models.TextField()
    file = models.FileField()
                            # TODO: Either prevent the file from changing after
                            # it has been uploaded, or make sure the old file
                            # is cleaned up if the file changes.
    ci_at = models.DateTimeField(editable=False, blank=True, null=True)
    dev_at = models.DateTimeField(editable=False, blank=True, null=True)
    stage_at = models.DateTimeField(editable=False, blank=True, null=True)
    prod_at = models.DateTimeField(editable=False, blank=True, null=True)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    def __getattr__(self, name):
        if name == 'release':
            if self.prod_at:
                return 'prod'

            elif self.stage_at:
                return 'stage'

            elif self.dev_at:
                return 'dev'

            elif self.ci_at:
                return 'ci'

            else:
                return 'new'

        raise AttributeError(name)

    # NOTE this does not save, make sure you .save() or something after,
    # otherwise the supporting info will no be set
    def checkfile(self, request_distro=None):
        if not self.file._file:  # no new file, nothing to look at, return
                                 # what we curently have, just to be sane
            if self.distroversion:
                return [self.distroversion.pk]
            else:
                return []

        else:  # new uploaded file, let's have a look
            import magic
            self._checkfile_ran = False

            (name, extension) = os.path.splitext(self.file.name)
            extension = extension[1:]  # remove the .

            if extension == 'deb':
                try:
                    (package, version, arch) = name.split('_')
                except ValueError:
                    raise ValidationError('Unrecognized deb file name Format')

                if arch == 'amd64':
                    arch = 'x86_64'
                elif arch not in ('i386', 'all'):
                    raise ValidationError('Unrecognized deb Arch')

            elif extension == 'rpm':
                try:
                    (package, version, release, arch) = re.match(
                        '(.+)-([^-]+)-([^-]+)\.(\w+)', name).groups()
                except ValueError:
                    raise ValidationError('Unrecognized rpm file name Format')

                if arch == 'noarch':
                    arch = 'all'
                elif arch not in ('i386', 'x86_64'):
                    raise ValidationError('Unrecognized rpm Arch')

                version = '%s-%s' % (version, release)

            else:
                raise ValidationError('Unrecognized file Extension')

            try:
                package = Package.objects.get(pk=package)
            except Package.DoesNotExist:
                raise ValidationError('Unable to find package "%s"' % package)

            m = magic.open(0)
            m.load()
            magic_type = m.file(self.file._file.temporary_file_path())
            if magic_type == 'Debian binary package (format 2.0)':
                package_type = 'deb'
            elif magic_type in ('RPM v3.0 bin noarch',
                                'RPM v3.0 bin i386/x86_64'):
                package_type = 'rpm'
            else:
                raise ValidationError('Unrecognized file Format')

            distroversion = None
            distroversion_list = []
            full_distroversion_list = []
            for tmp in DistroVersion.objects.filter(file_type=package_type):
                full_distroversion_list.append(tmp.pk)
                for name in tmp.release_names.split('\t'):
                    if name in version:
                        distroversion_list.append(tmp.pk)

            if request_distro:
                if request_distro in full_distroversion_list:
                    distroversion = request_distro

            elif len(distroversion_list) == 1:
                distroversion = distroversion_list[0]

            elif len(full_distroversion_list) == 1:
                distroversion = full_distroversion_list[0]

            if not distroversion:  # confused, punt to the caller
                if distroversion_list:
                    return distroversion_list
                else:
                    return full_distroversion_list

            # we found one and only one disto, we are taking it
            self.distroversion_id = distroversion
            self.package_type = package_type
            self.package = package
            self.type = extension
            self.arch = arch
            self.version = version
            self._checkfile_ran = True
            return [distroversion]

    def save(self, *args, **kwargs):
        try:  # _checkfile_ran isn't a real model member, trying to use it to
              # check if checkfile needs to run, incase it was run before
              # save()
            checkfile_ran = self._checkfile_ran
        except AttributeError:
            checkfile_ran = False

        if self.file._file and not checkfile_ran:
            options = self.checkfile()
            if not self._checkfile_ran:
                raise ValidationError(
                    'distroversion not set, run checkfile manually before ' +
                    'saving, aviable options "%s"' % options)

        super(PackageFile, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'PackageFile "%s"' % (self.file.name)

    class Meta:
        unique_together = (
            'package', 'distroversion', 'version', 'type', 'arch')
