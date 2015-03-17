from django.contrib import admin
from packrat.Repos.models import DistroVersion, Repo
from packrat.Repos.models import Package, PackageFile, Mirror

admin.site.register( DistroVersion )
admin.site.register( Repo )
admin.site.register( Mirror )
admin.site.register( Package )
admin.site.register( PackageFile )
