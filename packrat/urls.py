from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from cinp.django_plugin import DjangoAPI

from packrat import views

api = DjangoAPI( '/api/v1/' )
api.registerApp( 'Repos', 'v1' )

urlpatterns = patterns(
  '',
  url( r'^$', views.index, name='index' ),
  url( r'^repos/', include( 'packrat.Repos.urls' ) ),
  url( r'^gui/', include( 'packrat.GUI.urls', namespace='gui' ) ),
  url( r'^admin/', include( admin.site.urls ) ),
  url( r'^api/', include( api.urls ) ),
)

if settings.DEBUG:
  urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
