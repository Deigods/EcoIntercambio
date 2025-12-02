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
        # Hacer campos obligatorios
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    # Método para limpiar y validar first_name
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            # Quitamos espacios para validar, así permitimos "Ana Maria" pero no "Ana123"
            if not first_name.replace(' ', '').isalpha():
                raise ValidationError("El nombre solo debe contener letras.")
            return first_name.upper()
        return first_name

    # Método para limpiar y validar last_name
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            # Quitamos espacios para validar apellidos compuestos
            if not last_name.replace(' ', '').isalpha():
                raise ValidationError("El apellido solo debe contener letras.")
            return last_name.upper()
        return last_name

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and username.lower() == 'invitado':
            raise ValidationError("Este nombre de usuario no está permitido.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
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

        # Siempre read-only: agregando o modificando
        self.fields['fecha_publicacion'].initial = (
            self.instance.fecha_publicacion if self.instance and self.instance.pk
            else timezone.now().date()
        )
        self.fields['fecha_publicacion'].widget.attrs['readonly'] = True

        # Ocultar campo usuario para no admin
        if user and not user.is_superuser:
            self.fields.pop('usuario', None)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            return nombre.upper()
        return nombre

    def clean_color(self):
        color = self.cleaned_data.get('color')
        if color:
            if not color.replace(' ', '').isalpha():
                raise ValidationError("El color solo debe contener letras (sin números ni símbolos).")
            return color.upper()
        return color

class FormMensajes(forms.Form):
	mensaje = forms.CharField(widget=forms.Textarea(attrs = {

			"class": "formulario_ms",
			"placeholder":"Escribe tu mensaje"

		}))