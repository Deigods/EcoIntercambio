from django.contrib import admin
from .models import Estado, Tipo, Ubicacion, Producto, CanalUsuario, CanalMensaje, Canal

# Register your models here.

class CanalMensajeInline(admin.TabularInline):
    model = CanalMensaje
    extra = 1

class CanalUsuarioInline(admin.TabularInline):
    model = CanalUsuario
    extra = 1

class CanalAdmin(admin.ModelAdmin):
    inlines = [CanalMensajeInline, CanalUsuarioInline]

    class Meta:
        model = Canal


admin.site.register(Estado)
admin.site.register(Tipo)
admin.site.register(Ubicacion)
admin.site.register(Producto)
admin.site.register(Canal, CanalAdmin)
admin.site.register(CanalUsuario)
admin.site.register(CanalMensaje)