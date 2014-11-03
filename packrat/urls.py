from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin

from packrat import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^repos/', include('packrat.Repos.urls', namespace='repos')),
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
                           (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$',
                            'django.views.static.serve', {
                                'document_root': settings.MEDIA_ROOT}))
