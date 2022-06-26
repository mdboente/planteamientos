from socket import gaierror
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.db.models import Q
from apps.notification.emails import send_mail, test_connect_email
from random import choice
from django.core.exceptions import ObjectDoesNotExist
from apps.notification.notification import Notification
from django.contrib import messages



def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            if user.last_login is None:
                mensaje = 'Bienvenido a Gestión de Planteamiento, cualquier duda usted puede asesorarse ' \
                          'de la ayuda que le brindamos en la aplicación'
                messages.info(request, mensaje, 'BIENVENIDO !!!')
            auth.login(request, user)
            Notification.notify(request)
            return redirect('planteamientos:inbox', 0)
        else:
            mensaje = 'Ha tenido un error de autenticación por favor verifique el usuario y la contraseña'
            messages.error(request, mensaje, 'ERROR ! ')

    return render(request, 'login.html')


def olvidar_contrasegna(request):
    username = request.POST['username']
    email = request.POST['email']
    try:
        user = User.objects.get(Q(username=username) & Q(email=email))
    except ObjectDoesNotExist:
        mensaje = 'No exite un usuario con este nombre y correo'
        messages.error(request, mensaje, 'ERROR ! ')

    else:
        if test_connect_email():

            valores = '0123456789abcdefghijklmnopqrstuvVqyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            longitud, password = 8, ""
            password = password.join([choice(valores) for i in range(longitud)])
            user.set_password(password)
            user.save()
            mensaje = 'Hola {} !!, \r ' \
                      'Su solicitud se ha realizado con éxito, si desea acceder a la aplicación ' \
                      'Gestión de Planteamientos puede logearse con su nueva contraseña: {}' \
                .format(user.get_full_name(), password)
            email = send_mail('Cambio de contraseña', mensaje, email, send=False)
            try:
                email.send(fail_silently=False)
            except gaierror:
                mensaje2 = 'No se ha podido enviar el correo con su nueva contraseña. Intentelo de nuevo '
                messages.error(request, mensaje2, 'ERROR ! ')
            else:
                mensaje2 = 'Se le ha enviado un correo con su actual contraseña'
                messages.success(request, mensaje2, 'ÉXITO ! ')
        else:
            mensaje = 'Lo sentimos tenemos fallos con la conexión ' \
                      'host de correo inténtelo más tarde'
            messages.error(request, mensaje, 'ERROR ! ')

    return redirect('login')


def logout(request):
    auth.logout(request)
    return redirect('login')


def administrador(user):
    return user.is_staff


def secretario(user):
    return True if hasattr(user, 'seccionsindical') else False


def not_secretario(user):
    return True if not hasattr(user, 'seccionsindical') else False
