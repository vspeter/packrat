from django import forms

from packrat.Repos.models import PackageFile


class PackageFileForm(forms.ModelForm):
    class Meta:
        model = PackageFile
        fields = ['file', 'justification', 'provenance']
