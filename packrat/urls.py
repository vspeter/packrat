from django.conf.urls import patterns, include, url
from django.contrib import admin
from tastypie.api import Api

from packrat import views
from packrat.repos import api

v1_api = Api(api_name='v1')
v1_api.register(api.VersionResource())
v1_api.register(api.RepoResource())
v1_api.register(api.MirrorResource())
v1_api.register(api.PackageResource())
v1_api.register(api.PackageFileResource())


urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^repos/', include('packrat.repos.urls', namespace='repos')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
)
