from django.core.exceptions import PermissionDenied
from functools import wraps

def user_no_invitado(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.username == 'invitado':
            raise PermissionDenied("No tienes permiso para acceder a esta página.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
