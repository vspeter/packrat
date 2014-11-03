from django.contrib import admin
from packrat.repos import models

admin.site.register(models.Version)
admin.site.register(models.Repo)
admin.site.register(models.Mirror)
admin.site.register(models.Package)
admin.site.register(models.PackageFile)
