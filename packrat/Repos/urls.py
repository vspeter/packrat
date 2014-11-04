from django.conf.urls import patterns, url

from packrat.Repos import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^repo/(?P<repo_id>\d+)/$', views.repo, name='repo'),
    url(r'^mirror/(?P<mirror_id>[^/]+)/$', views.mirror, name='mirror'),
    url(r'^package/(?P<package_id>[^/]+)/$', views.package, name='package'),
    url(r'^packagefile/(?P<packagefile_id>\d+)/$', views.packagefile,
        name='packagefile'),
    url(r'^packagefile-add/$', views.packagefile_add, name='packagefile_add'),
    url(r'^packagefile-promote/(?P<packagefile_id>\d+)/$',
        views.packagefile_promote, name='packagefile_promote'),
    # for the mirror system to communicate with
    url(r'^sync/$', views.sync)
)
