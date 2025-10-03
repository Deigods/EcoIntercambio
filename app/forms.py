from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Producto
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username.lower() == 'invitado':  # bloquea "invitado" sin importar mayúsculas/minúsculas
            raise ValidationError("Este nombre de usuario no está permitido.")
        return username

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'estado', 'color', 'tipo', 'ubicacion', 'fecha_publicacion', 'imagen']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProductoForm, self).__init__(*args, **kwargs)

        # Establece la fecha actual como valor predeterminado para usuarios no admin
        if user and not user.is_superuser:
            self.fields['fecha_publicacion'].initial = timezone.now().date()
            self.fields['fecha_publicacion'].widget.attrs['readonly'] = True  # Hacer el campo solo lectura
        else:
            # Si es admin, permite elegir cualquier fecha
            self.fields['fecha_publicacion'].initial = timezone.now().date()
            self.fields['fecha_publicacion'].widget.attrs.pop('readonly', None)

        # Oculta el campo 'usuario' para usuarios no admin
        if user and not user.is_superuser:  
            self.fields.pop('usuario', None)


class FormMensajes(forms.Form):
	mensaje = forms.CharField(widget=forms.Textarea(attrs = {

			"class": "formulario_ms",
			"placeholder":"Escribe tu mensaje"

		}))