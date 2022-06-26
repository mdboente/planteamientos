from django.urls import path
from . import views

app_name = 'respuestas'
urlpatterns = [
    path('temporal/', views.temporal, name='temporal'),
    path('aprobacion/<int:evaluacion>/<int:respuesta_id>/', views.aprobacion, name='aprobacion')
]
