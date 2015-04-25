from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import RedirectView

from cinp.django_plugin import DjangoAPI

from packrat import views

api = DjangoAPI( '/api/v1/' )
api.registerApp( 'Repos', 'v1' )
api.registerFileUploader( 'FILES' )

urlpatterns = patterns(
  '',
  url( r'^$', views.index, name='index' ),
  url( r'^repos/', include( 'packrat.Repos.urls', namespace='repos' ) ),
  url( r'^admin/', include( admin.site.urls ) ),
  url( r'^api/', include( api.urls ) ),

  url( r'^ui/$', RedirectView.as_view( url='/files/ui/index.html', permanent=True ) ),
  url( r'^favicon.ico$', RedirectView.as_view( url='/files/ui/img/favicon.ico', permanent=True ) ),
)

if settings.DEBUG:
  urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
