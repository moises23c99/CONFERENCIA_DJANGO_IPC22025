from django import forms

class XMLUploadForm(forms.Form):
    archivo = forms.FileField(label="Archivo XML de Configuración", required=True)
