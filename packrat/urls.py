from django.conf.urls import patterns, include, url
from django.contrib import admin

from packrat import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^repos/', include('packrat.repos.urls', namespace='repos')),
    url(r'^admin/', include(admin.site.urls)),
)
