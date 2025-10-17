from django.urls import path, re_path
from . import views
from .views import (
    home,
    register,
    producto,
    registro,
    agregar_producto,
    listar_productos,
    modificar_producto,
    eliminar_producto,
    mensajes_privados,
    DetailMs,
    CanalDetailView,
    Inbox,
    export_to_excel_model,
    export_to_excel_estate,
    export_to_excel_type,
    export_to_excel_location,
    export_to_excel_friendly,
    export_to_excel,
)
from .chatbot_view import chatbot_view, chatbot_response

# UUID v4 para los canales de chat
UUID_CANAL_REGEX = r'canal/(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})'

urlpatterns = [
    # Home / productos
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("producto/<int:id>/", producto, name="producto"),
    path("registro/", registro, name="registro"),
    path("agregar_producto/", agregar_producto, name="agregar_producto"),
    path("listar-productos/", listar_productos, name="listar-productos"),
    path("modificar-producto/<int:id>/", modificar_producto, name="modificar-producto"),
    path("eliminar-producto/<int:id>/", eliminar_producto, name="eliminar_producto"),
    path('login-invitado/', views.login_invitado, name='login-invitado'), 

    # Mensajes / canales
    path("dm/<str:username>", mensajes_privados),
    path("ms/<str:username>", DetailMs.as_view(), name="detailms"),
    re_path(UUID_CANAL_REGEX, CanalDetailView.as_view()),
    path("inbox", Inbox.as_view(), name="inbox"),

    # Chatbot
    path("chatbot/", chatbot_view, name="chatbot"),
    path("chatbot/response/", chatbot_response, name="chatbot_response"),

    # PayPal: creación y captura + pantalla de éxito
    path("paypal/create/", views.paypal_create_order, name="paypal-create"),
    path("paypal/capture/", views.paypal_capture_order, name="paypal-capture"),
    path("suscripcion/exito/", views.subscription_success, name="subscription-success"),

    # Exportar productos a Excel
    path('exportar/ids/', export_to_excel_model, name='export_to_excel_product'),
    path('exportar/estados/', export_to_excel_estate, name='export_to_excel_estate'),
    path('exportar/tipos/', export_to_excel_type, name='export_to_excel_type'),
    path('exportar/ubicaciones/', export_to_excel_location, name='export_to_excel_location'),    
    path('exportar/nombres/', export_to_excel_friendly, name='export_to_excel_friendly'),

    path('exportar/',export_to_excel, name='export_options'),
]
