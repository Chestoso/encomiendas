# envios/forms.py

from django import forms
from .models import Encomienda
from clientes.models import Cliente
from rutas.models import Ruta



class EncomiendaForm(forms.ModelForm):
    """
    Formulario para registrar encomiendas.
    Cumple validación server-side y aplica estilos Bootstrap.
    """

    class Meta:
        model = Encomienda
        fields = '__all__'

        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: ENC-001',
                'required': True
            }),
            'remitente': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'destinatario': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'ruta': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.1',
                'required': True
            }),
            'costo_envio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Filtra solamente clientes y rutas activos.
        """
        super().__init__(*args, **kwargs)

        if 'remitente' in self.fields:
            self.fields['remitente'].queryset = Cliente.objects.filter(estado=1)

        if 'destinatario' in self.fields:
            self.fields['destinatario'].queryset = Cliente.objects.filter(estado=1)

        if 'ruta' in self.fields:
            self.fields['ruta'].queryset = Ruta.objects.filter(estado=1)

    def clean_peso_kg(self):
        """
        Validación server-side del peso.
        """
        peso = self.cleaned_data.get('peso_kg')

        if peso is not None and peso <= 0:
            raise forms.ValidationError('El peso debe ser mayor que 0.')

        return peso