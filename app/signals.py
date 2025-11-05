from django.db.models.signals import post_migrate
from django.contrib.auth.models import User
from .models import Estado, Tipo, Ubicacion
from django.dispatch import receiver

@receiver(post_migrate)
def create_invitado_user(sender, **kwargs):
    if not User.objects.filter(username='invitado').exists():
        User.objects.create_user(
            username='invitado',
            password='pass_invitado'
        )

@receiver(post_migrate)
def create_default_data(sender, **kwargs):
    if sender.name == 'app':
        Estado.objects.get_or_create(id=1, estado_name='Nuevo')
        Estado.objects.get_or_create(id=2, estado_name='Como nuevo')
        Estado.objects.get_or_create(id=3, estado_name='Usado')
        Estado.objects.get_or_create(id=4, estado_name='Reacondicionado')
        Estado.objects.get_or_create(id=5, estado_name='Dañado')
        Estado.objects.get_or_create(id=6, estado_name='Para repuestos')

        Tipo.objects.get_or_create(id=1, tipo_objeto='Electrónica')
        Tipo.objects.get_or_create(id=2, tipo_objeto='Electrodomésticos')
        Tipo.objects.get_or_create(id=3, tipo_objeto='Celulares')
        Tipo.objects.get_or_create(id=4, tipo_objeto='Computación')
        Tipo.objects.get_or_create(id=5, tipo_objeto='Accesorios tecnológicos')
        Tipo.objects.get_or_create(id=6, tipo_objeto='Ropa')
        Tipo.objects.get_or_create(id=7, tipo_objeto='Calzado')
        Tipo.objects.get_or_create(id=8, tipo_objeto='Muebles')
        Tipo.objects.get_or_create(id=9, tipo_objeto='Decoración')
        Tipo.objects.get_or_create(id=10, tipo_objeto='Libros')
        Tipo.objects.get_or_create(id=11, tipo_objeto='Juguetes')
        Tipo.objects.get_or_create(id=12, tipo_objeto='Instrumentos musicales')
        Tipo.objects.get_or_create(id=13, tipo_objeto='Herramientas')
        Tipo.objects.get_or_create(id=14, tipo_objeto='Artículos deportivos')
        Tipo.objects.get_or_create(id=15, tipo_objeto='Vehiculos')
        Tipo.objects.get_or_create(id=16, tipo_objeto='Bicicletas')
        Tipo.objects.get_or_create(id=17, tipo_objeto='Videojuegos')
        Tipo.objects.get_or_create(id=18, tipo_objeto='Cámaras y fotografía')
        Tipo.objects.get_or_create(id=19, tipo_objeto='Artículos para el hogar')
        Tipo.objects.get_or_create(id=20, tipo_objeto='Mascotas y accesorios')
        Tipo.objects.get_or_create(id=21, tipo_objeto='Otros')

        Ubicacion.objects.get_or_create(id=1, ubicacion_name='Región de Arica y Parinacota')
        Ubicacion.objects.get_or_create(id=2, ubicacion_name='Región de Tarapacá')
        Ubicacion.objects.get_or_create(id=3, ubicacion_name='Región de Antofagasta')
        Ubicacion.objects.get_or_create(id=4, ubicacion_name='Región de Atacama')
        Ubicacion.objects.get_or_create(id=5, ubicacion_name='Región de Coquimbo')
        Ubicacion.objects.get_or_create(id=6, ubicacion_name='Región de Valparaíso')
        Ubicacion.objects.get_or_create(id=7, ubicacion_name='Región Metropolitana de Santiago')
        Ubicacion.objects.get_or_create(id=8, ubicacion_name='Región del Libertador General Bernardo O’Higgins')
        Ubicacion.objects.get_or_create(id=9, ubicacion_name='Región del Maule')
        Ubicacion.objects.get_or_create(id=10, ubicacion_name='Región de Ñuble')
        Ubicacion.objects.get_or_create(id=11, ubicacion_name='Región del Biobío')
        Ubicacion.objects.get_or_create(id=12, ubicacion_name='Región de La Araucanía')
        Ubicacion.objects.get_or_create(id=13, ubicacion_name='Región de Los Ríos')
        Ubicacion.objects.get_or_create(id=14, ubicacion_name='Región de Los Lagos')
        Ubicacion.objects.get_or_create(id=15, ubicacion_name='Región de Aysén del General Carlos Ibáñez del Campo')
        Ubicacion.objects.get_or_create(id=16, ubicacion_name='Región de Magallanes y de la Antártica Chilena')