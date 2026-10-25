from django import forms
from .models import Producto, Cliente, Emisor, MovimientoInventario
from .validators import validar_identificacion_ecuador


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'descripcion', 'precio_unitario', 'tarifa_iva', 'stock', 'stock_minimo', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. PROD-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre descriptivo'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Detalles adicionales (opcional)'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'tarifa_iva': forms.Select(attrs={'class': 'form-select'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'min': '0'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_identificacion', 'identificacion', 'nombres', 'email', 'telefono', 'direccion']
        widgets = {
            'tipo_identificacion': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_identificacion'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula (10 dígitos) o RUC (13 dígitos)'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres y Apellidos o Razón Social'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 0991234567'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección domiciliaria'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_identificacion')
        numero = cleaned_data.get('identificacion')

        if tipo and numero:
            try:
                validar_identificacion_ecuador(tipo, numero)
            except Exception as e:
                self.add_error('identificacion', str(e))

        return cleaned_data


class EmisorForm(forms.ModelForm):
    class Meta:
        model = Emisor
        fields = [
            'ruc', 'razon_social', 'nombre_comercial', 'direccion_matriz',
            'establecimiento', 'punto_emision', 'secuencial_actual',
            'tarifa_iva_defecto', 'obligado_contabilidad', 'es_contribuyente_rimpe'
        ]
        widgets = {
            'ruc': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 13}),
            'razon_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_comercial': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_matriz': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'establecimiento': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 3}),
            'punto_emision': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 3}),
            'secuencial_actual': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'tarifa_iva_defecto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'obligado_contabilidad': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'es_contribuyente_rimpe': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InventarioMovimientoForm(forms.Form):
    TIPO_OPCIONES = [
        ('INGRESO', 'Ingreso / Entrada (Sumar al stock existente)'),
        ('AJUSTE', 'Ajuste Directo (Fijar nuevo stock físico)'),
    ]

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(activo=True),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'select_producto_ajuste'}),
        empty_label="Seleccione un producto..."
    )
    tipo_operacion = forms.ChoiceField(
        choices=TIPO_OPCIONES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='INGRESO'
    )
    cantidad = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '1', 'placeholder': 'Cantidad'})
    )
    motivo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Factura de compra proveedor #123 / Conteo físico'})
    )
