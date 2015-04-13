from django.conf.urls import patterns, url

from packrat.Repos import views

urlpatterns = patterns(
    '',
    url(r'^sync/$', views.sync)
)
