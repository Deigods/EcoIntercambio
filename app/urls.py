from django.contrib import admin
from django.urls import path, re_path
from .views import home, register, producto, registro, agregar_producto, listar_productos, modificar_producto, eliminar_producto, mensajes_privados, DetailMs, CanalDetailView, Inbox

UUID_CANAL_REGEX = r'canal/(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})'

urlpatterns = [
    path('', home, name="home"),
    path('register/', register, name="register"),
    path('producto/<int:id>/', producto, name="producto"),
    path('registro/', registro, name="registro"),
    path('agregar_producto/', agregar_producto, name="agregar_producto"),
    path('listar-productos/', listar_productos, name="listar-productos"),
    path('modificar-producto/<int:id>/', modificar_producto, name="modificar-producto"),
    path('eliminar-producto/<int:id>/', eliminar_producto, name='eliminar_producto'),
    path('dm/<str:username>', mensajes_privados),
    path('ms/<str:username>', DetailMs.as_view(), name="detailms"),
    re_path(UUID_CANAL_REGEX, CanalDetailView.as_view()),
    path("inbox", Inbox.as_view(), name="inbox"),
]