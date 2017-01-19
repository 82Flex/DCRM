from django import forms


class UploadForm(forms.Form):
    package = forms.FileField()
