from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.notification.emails import send_mail
from apps.mixin.login import administrador
from ..mixin import utils
from django.contrib import auth
from ..notification.notification import Notification
from django.contrib import messages


@user_passes_test(administrador, login_url='login')
@login_required(login_url='login')
def mostrar_usuarios(request) -> HttpResponse:
    users = User.objects.all()

    if request.method == "GET":
        x = request.GET.get('buscar', '')
        users = users.filter(Q(username__icontains=x)
                             | Q(first_name__icontains=x)
                             | Q(last_name__icontains=x)
                             | Q(email__icontains=x))

    return render(request, 'usuarios/mostrar_usuarios.html', {'users': users})


@user_passes_test(administrador, login_url='login')
@login_required(login_url='login')
def registrar_usuario(request) -> HttpResponse:
    if request.method == 'POST':
        Datos = {key: request.POST[key] for key in request.POST
                 if key == 'username' or key == 'password'
                 or key == 'last_name' or key == 'first_name' or key == 'email'}
        try:
            user = User.objects.create_user(**Datos)
        except IntegrityError:
            messages.error(request, 'Usted ha cometido un error completando el formulario. ', 'ERROR !')
        else:
            if 'admin' in request.POST:
                user.is_staff = True
            if 'superuser' in request.POST:
                user.is_superuser = True
                user.is_staff = True
            user.save()

            mensaje = "Usted ha sido registrado en el Sistema, Gestión de Planteamientos, puede acceder al mismo mediante la url http://planteamientos.vcl.etecsa.cu/planteamientos, por medidas de seguridad debe cambiar su contraseña en el primer inicio de sesión, para esto puede acceder al link (olvido su contraseña?) o editarla mediante la configuración de su perfil de usuario una vez que se encuentre logueado con los siguientes datos: \n usuario: %s \n contraseña: %s \n" % (user.username, Datos['password'])

            send_mail('Nuevo Usuario', mensaje, request.POST['email'])
            messages.success(request, 'Se ha creado el usuario {} correctamente'
                             .format(user.get_full_name()), 'ÉXITOS !')
            return redirect('usuarios:mostrar_usuarios')

    return render(request, 'usuarios/registrar_usuario.html')


@user_passes_test(administrador, login_url='login')
@login_required(login_url='login')
def eliminar_usuario(request, id_usuario: int) -> HttpResponse:
    usuario = get_object_or_404(User, pk=id_usuario)

    if usuario.is_superuser:
        if request.user.id == usuario.id:
            mensaje = 'Usted no puede eliminarse, si no desea formar parte de la aplicación' \
                      ' debe contactar a otro administrador'
            messages.warning(request, mensaje, 'ADVERTENCIA !! ')
            return redirect('usuarios:mostrar_usuarios')
        mensaje = 'Se ha eliminado un usuario administrador de la aplicación '
        messages.warning(request, mensaje, 'ADVERTENCIA !! ')


    else:
        mensaje = 'se ha eliminado el usuario {}'.format(usuario.get_full_name())
        messages.success(request, mensaje, 'ÉXITOS !')
    usuario.delete()
    return redirect('usuarios:mostrar_usuarios')


@login_required(login_url='login')
def editar_usuario(request, id_usuario: int, roll: int) -> HttpResponse:
    usuario = get_object_or_404(User, pk=id_usuario)
    error_email = False
    if request.user == usuario or request.user.is_staff:
        if request.method == "POST":
            try:
                usuario.username = request.POST["username"]
                usuario.email = request.POST["email"]
                if any(usuario.email == user.email for user in User.objects.exclude(id=id_usuario)):
                    error_email = True
                    raise IntegrityError
                usuario.last_name = request.POST["last_name"]
                usuario.first_name = request.POST["first_name"]

                # Activo
                if 'activo' in request.POST:
                    usuario.is_active = True
                else:
                    usuario.is_active = False
                # Super usuario
                if 'superuser' in request.POST:
                    usuario.is_superuser = True
                else:
                    usuario.is_superuser = False

                # Administrador
                if 'admin' in request.POST:
                    usuario.is_staff = True
                else:
                    usuario.is_staff = False

                usuario.save()
            except IntegrityError:
                mensaje = 'ya existe un usuario con este '
                messages.error(request, mensaje + 'email' if error_email else 'nombre de usuario', 'ERROR ! ')
            else:
                mensaje_email = 'Advertencia !!. Su perfil ha sido editado por el usuario {}: ' \
                                'le recomendamos que vaya a nuestra aplicación para que se serciore de su ' \
                                'nueva información personal'.format(request.user)
                send_mail('GESTIÓN PLANTEAMIENTO', mensaje_email, usuario.email)

                mensaje = 'El usuario {} se ha editado correctamente'.format(usuario.username)
                messages.success(request, mensaje, 'ÉXITOS !')

                return redirect('usuarios:mostrar_usuarios')

        return render(request, 'usuarios/editar_usuario.html', locals())
    else:
        return redirect('login')


def profile(request):
    perfil = utils.UsuarioLogin(request)
    planteamientos = perfil.plant(limit=10, estado=None)
    estado = perfil.por_ciento()
    if len(planteamientos) != 0:
        ninguno = True

    return render(request, 'usuarios/perfil.html', locals())


def cambio_password(request):
    error = False
    if request.method == "POST":
        if request.POST['password'] == request.POST['password2']:
            user = get_object_or_404(User, id=request.user.id)
            user.set_password(request.POST['password'])
            user.save()
            auth.login(request, user)
            Notification.notify(request)
            mensaje = 'Su contraseña se ha cambiado correctamente'
            messages.info(request, mensaje, 'ÉXITOS !')
            return redirect('usuarios:editar_usuario', request.user.id, 0)
        else:
            messages.error(request, 'Las contraseñas no son coincidentes', 'ERROR !! ')

    return render(request, 'usuarios/cambio_password.html', {'error': error})


def ayuda(request):
    return render(request, 'usuarios/ayuda.html')
