from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from tastypie.api import Api

from packrat import views
from packrat.Repos import api

v1_api = Api(api_name='v1')
v1_api.register(api.DistroVersionResource())
v1_api.register(api.RepoResource())
v1_api.register(api.MirrorResource())
v1_api.register(api.PackageResource())
v1_api.register(api.PackageFileResource())


urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^repos/', include('packrat.Repos.urls', namespace='repos')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
                           (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$',
                            'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT}))
