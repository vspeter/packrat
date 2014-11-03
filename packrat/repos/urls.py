from django.conf.urls import patterns, url

from packrat.repos import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^repo/(?P<repo_id>\d+)/$', views.repo, name='repo'),
    url(r'^mirror/(?P<mirror_id>[^/]+)/$', views.mirror, name='mirror'),
    url(r'^package/(?P<package_id>[^/]+)/$', views.package, name='package'),
    url(r'^file/(?P<file>\d+)/$', views.file, name='file'),
    url(r'^file-add/$', views.file, name='file'),
    url(r'^file-promote/(?P<file>\d+)/$',
        views.file_promote, name='file_promote'),
    # for the mirror system to communicate with
    url(r'^sync/$', views.sync)
)
