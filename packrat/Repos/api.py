from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
from tastypie.fields import ToManyField, ManyToManyField, ForeignKey
from tastypie.http import HttpGone, HttpMultipleChoices

from packrat.Repos import models


class DistroVersionResource(ModelResource):
    class Meta:
        queryset = models.DistroVersion.objects.all()
        resource_name = 'distroversion'


class PackageResource(ModelResource):
    packagefile_list = ToManyField('packrat.Repos.api.PackageFileResource',
                                   'packagefile_set')

    class Meta:
        queryset = models.Package.objects.all()
        resource_name = 'package'

    def build_filters(self, filters=None):
        result = super(PackageResource, self).build_filters(filters=filters)
        try:
            result.update(filters['__repo__packages__'].package_queryset_parms)
        except (KeyError, TypeError):
            pass

        return result


class PackageFileResource(ModelResource):
    distroversion = ForeignKey(DistroVersionResource,
                               'distroversion')
    package = ForeignKey(PackageResource, 'package')

    class Meta:
        queryset = models.PackageFile.objects.all()
        resource_name = 'packagefile'

    def build_filters(self, filters=None):
        result = super(PackageFileResource, self).build_filters(filters=filters)
        try:
            result['package_id'] = filters['__repo__files_package__']
            parms = filters['__repo__files__'].package_queryset_parms
            for key in parms:
                result[key.replace('packagefile__', '')] = parms[key]
        except (KeyError, TypeError):
            pass

        return result

    def dehydrate(self, bundle):
        bundle.data['release'] = bundle.obj.release
        return bundle


class RepoResource(ModelResource):
    distroversion_list = ManyToManyField(DistroVersionResource,
                                         'distroversion_list')

    class Meta:
        queryset = models.Repo.objects.all()
        resource_name = 'repo'

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/(?P<pk>.*?)/packages%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_packages'), name='api_get_packages'),
            url(r'^(?P<resource_name>%s)/(?P<pk>.*?)/files/' %
                self._meta.resource_name +
                r'(?P<package_pk>.*?)%s$' % trailing_slash(),
                self.wrap_view('get_files'), name='api_get_files'),
        ]

    def get_packages(self, request, **kwargs):
        try:
            bundle = self.build_bundle(data={'pk': kwargs['pk']},
                                       request=request)
            obj = self.obj_get(bundle=bundle,
                               **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices('More than one resource' +
                                       'is found at this URI.')

        package_resource = PackageResource()
        return package_resource.get_list(request, __repo__packages__=obj)

    def get_files(self, request, **kwargs):
        package_pk = kwargs['package_pk']
        del kwargs['package_pk']
        try:
            bundle = self.build_bundle(data={'pk': kwargs['pk']},
                                       request=request)
            obj = self.obj_get(bundle=bundle,
                               **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return HttpGone()
        except MultipleObjectsReturned:
            return HttpMultipleChoices('More than one resource' +
                                       'is found at this URI.')

        package_resource = PackageFileResource()
        return package_resource.get_list(request,
                                         __repo__files__=obj,
                                         __repo__files_package__=package_pk)


class MirrorResource(ModelResource):
    repo_list = ManyToManyField(RepoResource,
                                'repo_list')

    class Meta:
        queryset = models.Mirror.objects.all()
        resource_name = 'mirror'
