from django import forms

from packrat.repos.models import PackageFile


class PackageFileForm(forms.ModelForm):
    class Meta:
        model = PackageFile
        fields = ['file', 'justification', 'provenance']
