from django.urls import path
from . import views

app_name = 'planteamientos'
urlpatterns = [

    path('mostrar/<int:todos>', views.planteamiento, name='planteamiento'),
    path('inbox/<int:planteamiento_id>/', views.inbox, name='inbox'),
    path('crear/', views.crear_planteamiento, name='crear_planteamiento'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),
    path('editar/<id_planteamiento>/', views.editar_planteamiento, name='editar'),
    path("import/xlsx/", views.PlanteamientosImportXLSXService.as_view(),
         name="xlsx")

]
