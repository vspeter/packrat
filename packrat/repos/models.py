import os
import re
from django.core.exceptions import ValidationError
from django.db import models

MANAGER_TYPE_CHOICES = (('apt', 'apt'), ('yum', 'yum'), ('zypper', 'zypper'))
FILE_TYPE_CHOICES = (('deb', 'deb'), ('rpm', 'rpm'))
FILE_ARCH_CHOICES = (('x86_64', 'x86_64'), ('i386', 'i386'), ('all', 'all'))
RELEASE_TYPE_CHOICES = (
    ('ci', 'ci'),
    ('dev', 'dev'),
    ('stage', 'stage'),
    ('prod', 'prod')
)

# there is no ubuntu distro, it shares the same version space as debian
DISTRO_CHOICES = (
    ('debian', 'debian'),
    ('centos', 'centos'),
    ('rhel', 'rhel'),
    ('sles', 'sles')
)


class Version(models.Model):
    distro = models.CharField(max_length=6, choices=DISTRO_CHOICES)
    version = models.CharField(max_length=10)
    # release names are ' ' delimited, things like el5, trusty,
    # something that is in filename that tells what version it belongs to
    release_names = models.CharField(max_length=100)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    def __unicode__(self):
        return 'Version "%s" of "%s"' % (self.version, self.distro)

    class Meta:
        unique_together = ('distro', 'version')


class Repo(models.Model):
    version_list = models.ManyToManyField(Version)
    manager_type = models.CharField(max_length=6, choices=MANAGER_TYPE_CHOICES)
    description = models.CharField(max_length=200)
    release_type = models.CharField(max_length=7, choices=RELEASE_TYPE_CHOICES)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    def __getattr__(self, name):
        if name == 'package_list':
            if self.manager_type == 'deb':
                qs = Package.objects.filter(packagefile__type='deb')

            elif self.manager_type in ('yum', 'zypper'):
                qs = Package.objects.filter(packagefile__type='rpm')

            else:
                qs = Package.objects.none()

            if self.release_type == 'ci':
                qs = qs.filter(
                    packagefile__ci_at__isnull=False,
                    packagefile__dev_at__isnull=True,
                    packagefile__prod_at__isnull=True
                ).distinct()

            elif self.release_type == 'dev':
                qs = qs.filter(
                    packagefile__dev_at__isnull=False,
                    packagefile__prod_at__isnull=True
                ).distinct()

            elif self.release_type == 'prod':
                qs = qs.filter(
                    packagefile__prod_at__isnull=False).distinct()

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
    version = models.CharField(max_length=50, editable=False)
    type = models.CharField(
        max_length=3, editable=False, choices=FILE_TYPE_CHOICES)
    arch = models.CharField(
        max_length=5, editable=False, choices=FILE_ARCH_CHOICES)
    justification = models.TextField()
    provenance = models.TextField()
    file = models.FileField()
    ci_at = models.DateTimeField(blank=True, null=True)
    dev_at = models.DateTimeField(blank=True, null=True)
    stage_at = models.DateTimeField(blank=True, null=True)
    prod_at = models.DateTimeField(blank=True, null=True)
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

    def save(self, *args, **kwargs):
        # new uploaded file, let's have a look
        if self.file._file:
            import magic

            (name, extension) = os.path.splitext(self.file.name)
            extension = extension[1:]  # remove the .

            if extension == 'deb':
                try:
                    (package, version, arch) = name.split('_')
                except ValueError:
                    raise ValidationError('Unrecognised deb file name Format')

                if arch == 'amd64':
                    arch = 'x86_64'
                elif arch not in ('i386', 'all'):
                    raise ValidationError('Unrecognised deb Arch')

            elif extension == 'rpm':
                try:
                    (package, version, release, arch) = re.match(
                        '(.+)-([^-]+)-([^-]+)\.(\w+)', name)
                except ValueError:
                    raise ValidationError('Unrecognised rpm file name Format')

                if arch == 'noarch':
                    arch = 'all'
                elif arch not in ('i386', 'x86_64'):
                    raise ValidationError('Unrecognised rpm Arch')

                version = '%s-%s' % (version, release)

            else:
                raise ValidationError('Unrecognised file Extension')

            try:
                package = Package.objects.get(pk=package)
            except Package.DoesNotExist:
                raise ValidationError('Unable to find package "%s"' % package)

            m = magic.open(0)
            m.load()
            magic_type = m.file(self.file._file.temporary_file_path())
            if magic_type == 'Debian binary package (format 2.0)':
                self.package_type = 'deb'
            elif magic_type in (
                    'RPM v3.0 bin noarch', 'RPM v3.0 bin i386/x86_64'):
                self.package_type = 'rpm'
            else:
                raise ValidationError('Unreconised file Format')

            self.package = package
            self.type = extension
            self.arch = arch
            self.version = version

        super(PackageFile, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'PackageFile "%s" of "%s"' % (self.version, self.package)

    class Meta:
        unique_together = ('package', 'version', 'type', 'arch')
