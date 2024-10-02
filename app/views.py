from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import CustomUserCreationForm, ProductoForm, FormMensajes
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Producto, CanalMensaje, CanalUsuario, Canal
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse

from django.core.exceptions import PermissionDenied

from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormMixin

from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import FormMixin

from django.views.generic import View

class Inbox(View):
	def get(self, request):

		inbox = Canal.objects.filter(canalusuario__usuario__in=[request.user.id])


		context = {

			"inbox":inbox
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

            # Verificar si la solicitud es AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'mensaje': canal_obj.texto,
                    'username': canal_obj.usuario.username
                }, status=201)
            
            # Si no es una solicitud AJAX, continuar con el flujo normal
            return super().form_valid(form)
        
        # Si el formulario no es válido
        return super().form_invalid(form)



class CanalDetailView(LoginRequiredMixin, CanalFormMixin, DetailView):
    template_name = 'mensajes/detail.html'
    queryset = Canal.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        obj = context['object']
        print(obj)

        if self.request.user not in obj.usuarios.all():
            raise PermissionDenied
        
        context['canal_miembro'] = self.request.user in obj.usuarios.all()
        return context

    def get_queryset(self):

        usuario = self.request.user
        username = usuario.username

        qs = Canal.objects.all().filtrar_por_username(username)
        return qs

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



def home(request):
    query = request.GET.get('query', '')  # Obtiene el valor de búsqueda
    productos = Producto.objects.all()

    # Filtrar solo si hay una consulta
    if query:
        productos = productos.filter(nombre__istartswith=query)  # Filtrar por nombres que comiencen con el término

    return render(request, 'app/index.html', {
        'productos': productos,
        'query': query  # Pasar la consulta para que se mantenga en la barra de búsqueda
    })

def register(request):
    return render(request, 'app/register.html');

def producto(request, id):
    entidad = get_object_or_404(Producto, id = id)

    data = {
        'entidad': entidad
    }
    return render(request, 'app/producto.html', data);

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

def agregar_producto(request):
    
    data = {
        'form': ProductoForm(user=request.user)  # Pasar el usuario aquí
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, files=request.FILES, user=request.user)

        if formulario.is_valid():
            formulario.instance.usuario = request.user  # Asignar el usuario actual
            formulario.save()
            messages.success(request, "Agregado correctamente")
            return redirect('listar-productos')  # Redirige a la lista de productos
        else:
            data["form"] = formulario

    return render(request, 'app/producto/agregar.html', data)

def listar_productos(request):
    productos = Producto.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(productos, 5)
        productos = paginator.page(page)
    except:
        raise Http404

    data = {
        'entity' : productos,
        'paginator' : paginator
    }
    return render(request, 'app/producto/listar.html', data)

def modificar_producto(request, id):

    producto = get_object_or_404(Producto, id=id)

    data = {
        'form': ProductoForm(instance = producto)
    }

    if request.method == 'POST':
        formulario = ProductoForm(data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Modificado correctamente")
            return redirect(to='listar-productos')
        else:
            data["form"] = formulario

    return render(request, 'app/producto/modificar.html', data);

def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    messages.success(request, "Eliminado correctamente")
    return redirect(to='listar-productos')


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
