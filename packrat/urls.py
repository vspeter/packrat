from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from tastypie.api import Api

from packrat import auth
from packrat import views
from packrat.Repos import api

auth_api = Api(api_name='v1')
auth_api.register(auth.UserResource())

repo_api_v1 = Api(api_name='v1')
repo_api_v1.register(api.DistroVersionResource())
repo_api_v1.register(api.RepoResource())
repo_api_v1.register(api.MirrorResource())
repo_api_v1.register(api.PackageResource())
repo_api_v1.register(api.PackageFileResource())


urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^repos/', include('packrat.Repos.urls', namespace='repos')),
    url(r'^gui/', include('packrat.GUI.urls', namespace='gui')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^auth/', include(auth_api.urls)),
    url(r'^api/', include(repo_api_v1.urls)),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
