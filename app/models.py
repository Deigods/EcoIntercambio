from django.db import models
import uuid
from django.contrib.auth.models import User
from django.apps import apps
from django.db.models import Count
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# ---------------------------
# Notificaciones / catálogo
# ---------------------------
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
    # OJO: default=1 solo si sabes que existe ese usuario; idealmente quítalo si no te hace falta
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.nombre


# ---------------------------
# Mensajería (canales)
# ---------------------------
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
    # (dejamos tiempo de ChatModel; si quieres, puedes quitar este campo duplicado)
    tiempo = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username}: {self.texto[:20]}'


class CanalUsuario(ChatModel):
    canal = models.ForeignKey("Canal", null=True, on_delete=models.SET_NULL)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.usuario.username} en {self.canal_id}'


class canalQuerySet(models.QuerySet):
    def solo_uno(self):
        return self.annotate(num_usuarios=Count("usuarios")).filter(num_usuarios=1)

    def solo_dos(self):
        return self.annotate(num_usuarios=Count("usuarios")).filter(num_usuarios=2)

    def filtrar_por_username(self, username):
        return self.filter(canalusuario__usuario__username=username)


class CanalManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return canalQuerySet(self.model, using=self._db)

    def filtrar_ms_por_privado(self, username_a, username_b):
        return (
            self.get_queryset()
            .solo_dos()
            .filtrar_por_username(username_a)
            .filtrar_por_username(username_b)
        )

    def obtener_o_crear_canal_usuario_actual(self, user):
        # << FIX: aquí antes usabas User.username (clase), debe ser user.username (instancia)
        qs = self.get_queryset().solo_uno().filtrar_por_username(user.username)
        if qs.exists():
            return qs.order_by("tiempo").first(), False

        canal_obj = Canal.objects.create()
        CanalUsuario.objects.create(usuario=user, canal=canal_obj)
        return canal_obj, True

    def obtener_o_crear_canal_ms(self, username_a, username_b):
        qs = self.filtrar_ms_por_privado(username_a, username_b)
        if qs.exists():
            return qs.order_by("tiempo").first(), False

        UserModel = apps.get_model("auth", model_name='User')
        try:
            usuario_a = UserModel.objects.get(username=username_a)
            usuario_b = UserModel.objects.get(username=username_b)
        except UserModel.DoesNotExist:
            return None, False

        obj_canal = Canal.objects.create()
        CanalUsuario.objects.bulk_create([
            CanalUsuario(usuario=usuario_a, canal=obj_canal),
            CanalUsuario(usuario=usuario_b, canal=obj_canal),
        ])
        return obj_canal, True


class Canal(ChatModel):
    usuarios = models.ManyToManyField(User, blank=True, through=CanalUsuario)
    objects = CanalManager()

    def __str__(self):
        return f'Canal {self.id}'


# ---------------------------
# Suscripción / Perfil
# ---------------------------
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


# --- Señales para crear/garantizar Profile ---
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, instance, **kwargs):
    # En caso de usuarios antiguos sin profile
    Profile.objects.get_or_create(user=instance)
