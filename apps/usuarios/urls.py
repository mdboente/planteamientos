from django.urls import path
from . import users

app_name = 'usuarios'
urlpatterns = [

    path('mostrar', users.mostrar_usuarios, name='mostrar_usuarios'),
    path('registrar', users.registrar_usuario, name='registrar_usuario'),
    path('eliminar/<int:id_usuario>/', users.eliminar_usuario, name='eliminar_usuario'),
    path('editar/<int:id_usuario>/<int:roll>/', users.editar_usuario, name='editar_usuario'),
    path('perfil/', users.profile, name='perfil'),
    path('cambiarcontraseña/', users.cambio_password, name='cambio_password'),
    path('ayuda/', users.ayuda, name='ayuda'),

]
