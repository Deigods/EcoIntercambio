from django.apps import AppConfig

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        from django.contrib.auth.models import User
        # Crear usuario invitado si no existe
        if not User.objects.filter(username='invitado').exists():
            User.objects.create_user(
                username='invitado',
                password='pass_invitado'
            )