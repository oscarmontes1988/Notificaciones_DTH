# notificaciones/forms.py
from django import forms

class CargaExcelForm(forms.Form):
    archivo_excel = forms.FileField(
        label='Cargar Excel de J. Gregorio',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )