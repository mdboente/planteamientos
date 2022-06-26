from django.contrib import admin
from .models import *

# Register your models here.


class AdminUnidad(admin.ModelAdmin):
    list_display = ['nombre', 'responsable']


class AdminSeccion(admin.ModelAdmin):
    list_display = ['nombre', 'secretario', 'unidad']


admin.site.register(Procesos)
admin.site.register(Planteamiento)
admin.site.register(UnidadOrganizativa, AdminUnidad)
admin.site.register(SeccionSindical, AdminSeccion)
#admin.site.register(ContraRespuesta)
#admin.site.register(RespuestaTemporal)
#admin.site.register(HistorialRespuesta)



