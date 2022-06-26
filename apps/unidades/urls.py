from django.urls import path
from . import views

app_name = 'unidades'
urlpatterns = [

    path('listar/', views.listar, name='listar'),
    path('editar/', views.editar, name='editar'),
    path('eliminar/<int:unidad_id>/', views.eliminar, name='eliminar'),
    path('listar_seccion/', views.listar_seccion, name='listar_seccion'),
    path('editar_seccion/', views.editar_seccion, name='editar_seccion'),
    path('eliminar_seccion/<int:seccion_id>/', views.eliminar_seccion, name='eliminar_seccion')
]


