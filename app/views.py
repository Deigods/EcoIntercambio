from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import CustomUserCreationForm, ProductoForm, FormMensajes
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Producto, CanalMensaje, CanalUsuario, Canal, Ubicacion
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse

from django.core.exceptions import PermissionDenied

from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin

from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import FormMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Notificacion
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView
from .models import Notificacion
from django.http import Http404
from .models import Producto, Tipo

class Inbox(View):
    def get(self, request):
        # Marcar notificaciones como leídas al acceder al inbox
        Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)

        inbox = Canal.objects.filter(canalusuario__usuario__in=[request.user.id])
        context = {
            "inbox": inbox,
            "notificaciones_no_leidas": Notificacion.objects.filter(usuario=request.user, leido=False).count(),
        }

        return render(request, 'mensajes/inbox.html', context)


class CanalFormMixin(FormMixin):
    form_class = FormMensajes

    def get_success_url(self):
        return self.request.path

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied

        form = self.get_form()

        if form.is_valid():
            canal = self.get_object()
            usuario = self.request.user
            mensaje = form.cleaned_data.get("mensaje")
            canal_obj = CanalMensaje.objects.create(canal=canal, usuario=usuario, texto=mensaje)

            # Crear la notificación
            for miembro in canal.usuarios.exclude(id=usuario.id):  # Notificar a otros usuarios en el canal
                Notificacion.objects.create(usuario=miembro, mensaje=f"{usuario.username} te ha enviado un mensaje.")

            # Verificar si la solicitud es AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'mensaje': canal_obj.texto,
                    'username': canal_obj.usuario.username
                }, status=201)
            
            # Si no es una solicitud AJAX, continuar con el flujo normal
            return super().form_valid(form)
        
        return super().form_invalid(form)


class CanalDetailView(LoginRequiredMixin, CanalFormMixin, DetailView):
    template_name = 'mensajes/detail.html'
    queryset = Canal.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        canal = context['object']

        # Verificar si el usuario actual es miembro del canal
        if self.request.user not in canal.usuarios.all():
            raise PermissionDenied("No tienes permiso para ver este canal.")

        context['canal_miembro'] = self.request.user in canal.usuarios.all()
        return context

    def get_object(self, *args, **kwargs):
        username = self.kwargs.get("username")
        mi_username = self.request.user.username

        # Si el canal es de este usuario o pertenece a ambos, entonces lo mostramos
        canal, created = Canal.objects.obtener_o_crear_canal_ms(mi_username, username)

        if not canal or self.request.user not in canal.usuarios.all():
            raise Http404("Este canal no existe o no tienes acceso.")

        return canal

class DetailMs(LoginRequiredMixin, CanalFormMixin, DetailView):
    template_name = 'mensajes/detail.html'

    def get_object(self, *args, **kwargs):
        username = self.kwargs.get("username")
        mi_username = self.request.user.username
        canal, _ = Canal.objects.obtener_o_crear_canal_ms(mi_username, username)

        if username == mi_username:
            mi_canal, _ = Canal.objects.obtener_o_crear_canal_usuario_actual(self.request.user)
            return mi_canal

        if canal is None:
            raise Http404

        return canal

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        canal = self.get_object()
        context['mensaje_canal'] = canal.canalmensaje_set.all().order_by('tiempo')
        return context



@login_required
def home(request):
    query = request.GET.get('query', '')
    tipo_id = request.GET.get('tipo', '')
    ubicacion_id = request.GET.get('ubicacion', '')
    productos = Producto.objects.all()

    # Contar notificaciones no leídas
    notificaciones_no_leidas = Notificacion.objects.filter(usuario=request.user, leido=False).count()

    # Filtrar productos si hay una consulta
    if query:
        productos = productos.filter(nombre__istartswith=query)
    if tipo_id:
        productos = productos.filter(tipo_id=tipo_id)
    if ubicacion_id:
        productos = productos.filter(ubicacion_id=ubicacion_id)

    tipos = Tipo.objects.all()
    ubicaciones = Ubicacion.objects.all()  # Para el filtro de región

    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(productos, 6)
        productos = paginator.page(page)
    except:
        raise Http404

    return render(request, 'app/index.html', {
        'entity': productos,
        'paginator': paginator,
        'query': query,
        'tipos': tipos,
        'tipo_seleccionado': tipo_id,
        'notificaciones_no_leidas': notificaciones_no_leidas,
        'ubicaciones': ubicaciones,
        'ubicacion_seleccionada': ubicacion_id,
    })

def register(request):
    return render(request, 'app/register.html');

@login_required
def producto(request, id):
    entidad = get_object_or_404(Producto, id=id)
    data = {'entidad': entidad, 'latitud': entidad.latitud, 'longitud': entidad.longitud}
    return render(request, 'app/producto.html', data)

def registro(request):
    data = {
        'form': CustomUserCreationForm()
    }

    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            username = formulario.cleaned_data["username"]
            password = formulario.cleaned_data["password1"]
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Te has registrado correctamente")
                return redirect(to="home")
            else:
                messages.error(request, "Error en la autenticacion. Por favor, intentalo de nuevo.")
        data['form'] = formulario

    return render(request, 'registration/register.html', data);

@login_required
def agregar_producto(request):
    data = {
        'form': ProductoForm(user=request.user)
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, files=request.FILES, user=request.user)

        if formulario.is_valid():
            formulario.instance.usuario = request.user

            # Obtener y limpiar latitud y longitud
            latitude = request.POST.get('latitude', '').strip()
            longitude = request.POST.get('longitude', '').strip()

            # Verificar si los valores son válidos y convertir a float
            try:
                formulario.instance.latitud = float(latitude)
                formulario.instance.longitud = float(longitude)
            except ValueError:
                messages.error(request, "Latitud y longitud deben ser números válidos.")
                data['form'] = formulario
                return render(request, 'app/producto/agregar.html', data)

            formulario.save()
            messages.success(request, "Agregado correctamente")
            return redirect('listar-productos')
        else:
            data["form"] = formulario

    return render(request, 'app/producto/agregar.html', data)


@login_required
def listar_productos(request):
    # Filtrar los productos según el usuario
    if request.user.is_superuser:
        productos = Producto.objects.all()
    else:
        productos = Producto.objects.filter(usuario=request.user)

    query = request.GET.get('query', '')
    tipo_id = request.GET.get('tipo', '')
    ubicacion_id = request.GET.get('ubicacion', '')

    if query:
        productos = productos.filter(nombre__istartswith=query)
    if tipo_id:
        productos = productos.filter(tipo_id=tipo_id)
    if ubicacion_id:
        productos = productos.filter(ubicacion_id=ubicacion_id)

    tipos = Tipo.objects.all()
    ubicaciones = Ubicacion.objects.all()

    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(productos, 5)
        productos = paginator.page(page)
    except:
        raise Http404

    context = {
        'entity': productos,
        'query': query,
        'paginator': paginator,
        'tipos': tipos,
        'tipo_seleccionado': tipo_id,
        'ubicaciones': ubicaciones,
        'ubicacion_seleccionada': ubicacion_id,
    }
    return render(request, 'app/producto/listar.html', context)


@login_required
def modificar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    # Verificar si el usuario actual es el dueño del producto o es un superusuario
    if request.user != producto.usuario and not request.user.is_superuser:
        raise PermissionDenied("No tienes permiso para modificar este producto.")

    data = {
        'form': ProductoForm(instance=producto),
        'entidad': producto  # Para pasar los valores de latitud y longitud al template
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            # Obtener y limpiar latitud y longitud
            latitude = request.POST.get('latitude', '').strip()
            longitude = request.POST.get('longitude', '').strip()

            # Verificar si los valores son válidos y convertir a float
            try:
                if latitude:
                    producto.latitud = float(latitude)
                if longitude:
                    producto.longitud = float(longitude)
            except ValueError:
                messages.error(request, "Latitud y longitud deben ser números válidos.")
                data['form'] = formulario
                return render(request, 'app/producto/modificar.html', data)

            formulario.save()
            messages.success(request, "Modificado correctamente")
            return redirect('listar-productos')
        else:
            data["form"] = formulario

    return render(request, 'app/producto/modificar.html', data)

@login_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    # Verificar si el usuario tiene permiso para eliminar
    if request.user != producto.usuario and not request.user.is_superuser:
        raise PermissionDenied("No tienes permiso para eliminar este producto.")
    
    producto.delete()
    messages.success(request, "Producto eliminado correctamente")
    return redirect('listar-productos')


@login_required
def mensajes_privados(request, username, *args, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponse("Prohibido")

    mi_username = request.user.username
    canal, created = Canal.objects.obtener_o_crear_canal_ms(mi_username, username)

    if created:
        print("Si, fue creado")

    # Ordenar los mensajes aquí
    mensaje_canal = canal.canalmensaje_set.all().order_by('tiempo')

    context = {
        'canal': canal,
        'mensaje_canal': mensaje_canal,
        'usuarios_canal': canal.canalusuario_set.all(),
    }

    return render(request, 'mensajes/detail.html', context)



# --- PayPal / Suscripciones ---
import json
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersCaptureRequest
from .paypal_client import get_paypal_client
from .models import SubscriptionPayment  # Asegúrate de que existe este modelo

@login_required
def paypal_create_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    client = get_paypal_client()
    create_request = OrdersCreateRequest()
    create_request.prefer("return=representation")
    create_request.request_body({
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": settings.SUBSCRIPTION_CURRENCY,
                "value": str(settings.SUBSCRIPTION_PRICE.quantize(Decimal('1.00'))),
            },
            "description": settings.SUBSCRIPTION_DESCRIPTION,
        }]
    })

    try:
        response = client.execute(create_request)
        order = response.result
        return JsonResponse({"id": order.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def paypal_capture_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        body = {}

    order_id = body.get("orderID")
    if not order_id:
        return JsonResponse({"error": "Missing orderID"}, status=400)

    client = get_paypal_client()
    capture_request = OrdersCaptureRequest(order_id)
    capture_request.request_body({})

    try:
        response = client.execute(capture_request)
        result = response.result
        status = getattr(result, "status", "")

        # Guarda registro del pago
        SubscriptionPayment.objects.create(
            user=request.user,
            order_id=order_id,
            status=status,
            amount=settings.SUBSCRIPTION_PRICE,
            currency=settings.SUBSCRIPTION_CURRENCY,
            raw=json.loads(result.json()),
        )

        # Marca premium si se completó
        if status == "COMPLETED":
            profile = request.user.profile  # asumiendo modelo Profile OneToOne
            profile.is_premium = True
            profile.premium_since = timezone.now()
            profile.save()
            return JsonResponse({"status": "COMPLETED"})

        return JsonResponse({"status": status})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def subscription_success(request):
    return render(request, "app/subscription_success.html")
