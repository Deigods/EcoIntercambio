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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer obligatorio el correo
        self.fields['email'].required = True

    # Método para limpiar y convertir a mayúsculas el campo first_name
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            return first_name.upper()
        return first_name

    # Método para limpiar y convertir a mayúsculas el campo last_name
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            return last_name.upper()
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and username.lower() == 'invitado':
            raise ValidationError("Este nombre de usuario no está permitido.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # NOTA: Si quieres que el email también se guarde en mayúsculas,
        # puedes cambiar la línea de retorno a: return email.upper()
        if email:
             if User.objects.filter(email=email).exists():
                 raise ValidationError("Este correo ya está registrado.")
        return email

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'estado', 'color', 'tipo', 'ubicacion', 'fecha_publicacion', 'imagen']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Siempre read-only: agregando o modificando, admin o no admin
        self.fields['fecha_publicacion'].initial = (
            self.instance.fecha_publicacion if self.instance and self.instance.pk
            else timezone.now().date()
        )
        self.fields['fecha_publicacion'].widget.attrs['readonly'] = True

        # Ocultar campo usuario para no admin
        if user and not user.is_superuser:
            self.fields.pop('usuario', None)

    # Método para limpiar y convertir a MAYÚSCULAS el campo nombre (texto libre)
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            return nombre.upper()
        return nombre

    # Método para limpiar y convertir a MAYÚSCULAS el campo color (texto libre)
    def clean_color(self):
        color = self.cleaned_data.get('color')
        if color:
            return color.upper()
        return color

class FormMensajes(forms.Form):
	mensaje = forms.CharField(widget=forms.Textarea(attrs = {

			"class": "formulario_ms",
			"placeholder":"Escribe tu mensaje"

		}))