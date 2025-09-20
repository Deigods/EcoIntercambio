from django.db import models
import uuid
from django.contrib.auth.models import User

from django.apps import apps

from django.db.models import Count
from django.db import models
from django.contrib.auth.models import User

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notificación para {self.usuario.username} - {self.fecha_creacion}'

class Estado(models.Model):
    estado_name = models.CharField(max_length=40)

    def __str__(self):
        return self.estado_name

class Tipo(models.Model):
    tipo_objeto = models.CharField(max_length=45)

    def __str__(self):
        return self.tipo_objeto

class Ubicacion(models.Model):
    ubicacion_name = models.CharField(max_length=50)

    def __str__(self):
        return self.ubicacion_name

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    estado = models.ForeignKey('Estado', on_delete=models.PROTECT)
    color = models.CharField(max_length=30)
    tipo = models.ForeignKey('Tipo', on_delete=models.PROTECT)
    ubicacion = models.ForeignKey('Ubicacion', on_delete=models.PROTECT)
    fecha_publicacion = models.DateField()
    imagen = models.ImageField(upload_to='productos', null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Asume que el usuario con ID 1 es un admin o similar
    latitud = models.FloatField(null=True, blank=True)  # Nuevo campo para latitud
    longitud = models.FloatField(null=True, blank=True)  # Nuevo campo para longitud

    def __str__(self):
        return self.nombre


class ChatModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, db_index=True, editable=False)
    tiempo = models.DateTimeField(auto_now_add=True)
    actualizar = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CanalMensaje(ChatModel):
    canal = models.ForeignKey("Canal", on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    tiempo = models.DateTimeField(auto_now_add=True)

class CanalUsuario(ChatModel):
    canal = models.ForeignKey("Canal", null=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

class canalQuerySet(models.QuerySet):
    def solo_uno(self):
        return self.annotate(num_usuarios = Count("usuarios")).filter(num_usuarios=1)

    def solo_dos(self):
        return self.annotate(num_usuarios = Count("usuarios")).filter(num_usuarios=2)

    def filtrar_por_username(self, username):
        return self.filter(canalusuario__usuario__username= username)

class CanalManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return canalQuerySet(self.model, using=self._db)
    
    def filtrar_ms_por_privado(self, username_a, username_b):
        return self.get_queryset().solo_dos().filtrar_por_username(username_a).filtrar_por_username(username_b)

    def obtener_o_crear_canal_usuario_actual(self, user):
        qs = self.get_queryset().solo_uno().filtrar_por_username(User.username)

        if qs.exists():
            return qs.order_by("tiempo").first, False
        
        canal_obj = Canal.objects.create()
        CanalUsuario.objects.create(usuario=user, canal=canal_obj)
        return canal_obj, True

    def obtener_o_crear_canal_ms(self, username_a, username_b):
        qs = self.filtrar_ms_por_privado(username_a, username_b)

        if qs.exists():
            return qs.order_by("tiempo").first(), False #obj, created
        
        User = apps.get_model("auth", model_name='User')
        usuario_a, usuario_b = None, None

        try:
            usuario_a = User.objects.get(username=username_a)
        except User.DoesNotExist:
            return None, False
        
        try:
            usuario_b = User.objects.get(username=username_b)
        except User.DoesNotExist:
            return None, False
        

        if usuario_a == None or usuario_b == None:
            return None, False

        obj_canal = Canal.objects.create()
        canal_usuario_a = CanalUsuario(usuario=User.objects.get(username=username_a), canal = obj_canal)
        canal_usuario_b = CanalUsuario(usuario=User.objects.get(username=username_b), canal = obj_canal)
        CanalUsuario.objects.bulk_create([canal_usuario_a, canal_usuario_b])
        
        return obj_canal, True

class Canal(ChatModel):
    usuarios = models.ManyToManyField(User, blank=True, through=CanalUsuario)

    objects = CanalManager()


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_premium = models.BooleanField(default=False)
    premium_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

class SubscriptionPayment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    raw = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.status} - {self.amount} {self.currency}"
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
