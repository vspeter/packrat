from tastypie.resources import ModelResource
from packrat.Repos import models


class VersionResource(ModelResource):
    class Meta:
        queryset = models.Repo.objects.all()
        resource_name = 'version'


class RepoResource(ModelResource):
    class Meta:
        queryset = models.Repo.objects.all()
        resource_name = 'repo'


class MirrorResource(ModelResource):
    class Meta:
        queryset = models.Mirror.objects.all()
        resource_name = 'mirror'


class PackageResource(ModelResource):
    class Meta:
        queryset = models.Package.objects.all()
        resource_name = 'package'


class PackageFileResource(ModelResource):
    class Meta:
        queryset = models.Mirror.objects.all()
        resource_name = 'packagefile'
