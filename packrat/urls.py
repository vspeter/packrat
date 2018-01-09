from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

# api = DjangoAPI( '/api/v1/' )
# api.registerApp( 'Repos', 'v1.1' )

urlpatterns = [
    url( r'^$', RedirectView.as_view( url='/files/ui/index.html', permanent=True ) ),
    # url( r'^api/', include( api.urls ) ),
    url( r'^admin/', admin.site.urls ),
    url( r'^favicon.ico$', RedirectView.as_view( url='/files/ui/img/favicon.ico', permanent=True ) ),
]

if settings.DEBUG:
  urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
