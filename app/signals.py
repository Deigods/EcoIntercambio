from django.db.models.signals import post_migrate
from django.contrib.auth.models import User
from django.dispatch import receiver

@receiver(post_migrate)
def create_invitado_user(sender, **kwargs):
    if not User.objects.filter(username='invitado').exists():
        User.objects.create_user(
            username='invitado',
            password='pass_invitado'
        )
