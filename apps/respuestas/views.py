from django.db import IntegrityError
from django.shortcuts import redirect, get_object_or_404
from .models import *
from ..mixin import utils
from apps.planteamientos.models import Planteamiento
from apps.planteamientos.views import inbox
from django.contrib.auth.decorators import login_required, user_passes_test
from apps.mixin.login import not_secretario
from django.contrib import messages


@user_passes_test(not_secretario, login_url='login')
@login_required(login_url='login')
def temporal(request):
    planteamiento_id = request.POST['planteamiento_id']
    planteamiento = get_object_or_404(Planteamiento, id=planteamiento_id)
    if request.user.is_staff:
        historial = HistorialRespuesta()
        historial.descripcion = utils.Html.get_text(request.POST['respuesta'])
        historial.autor = request.user.get_full_name()
        historial.planteamiento_id = planteamiento_id
        historial.fecha = timezone.now().date()
        if 'Solucion' in request.POST: historial.planteamiento.estado = 'Solucionado'
        else: historial.planteamiento.estado = 'Pendiente'
        historial.planteamiento.save()
        historial.save()
    else:
        try:
            respuesta_temporal = RespuestaTemporal()
            respuesta_temporal.autor = request.user.get_full_name()
            respuesta_temporal.respuesta = utils.Html.get_text(request.POST['respuesta'])
            respuesta_temporal.planteamiento_id = planteamiento_id
            respuesta_temporal.save()

        except IntegrityError:
            mensaje = 'Ya este Planteamiento tiene una respuesta pendiente si desea puede ' \
                      'editarla pulsando el ícono de modificar '
            messages.error(request, mensaje, 'ERROR ! ')
        else:
            mensaje = 'Su respuesta se ha guardado y ha pasado al estado de evaluación'
            messages.success(request, mensaje, 'ÉXITO ! ')
            if 'Solucion' in request.POST: planteamiento.estado = 'Solucionado'
            else: planteamiento.estado = 'Pendiente'
            planteamiento.save()

    return redirect('planteamientos:inbox', planteamiento_id)


@user_passes_test(not_secretario, login_url='login')
@login_required(login_url='login')
def aprobacion(request, evaluacion, respuesta_id):
    error = False
    respuesta = get_object_or_404(RespuestaTemporal, id=respuesta_id)
    planteamiento = respuesta.planteamiento_id
    historial = HistorialRespuesta()
    if evaluacion == 1:
        try:
            historial.descripcion = respuesta.respuesta
            historial.planteamiento_id = respuesta.planteamiento_id
            historial.fecha = respuesta.fecha
            historial.autor = respuesta.autor
            historial.save()
            respuesta.delete()
            mensaje = 'La respuesta ha sido enviada al la Sección Sindical {}'\
                .format(historial.planteamiento.seccion_sindical.nombre)
            messages.success(request, mensaje, 'ÉXITOS ! ')
        except IntegrityError:
            error = True
        return redirect('planteamientos:inbox', historial.planteamiento_id
                        if not error else respuesta.planteamiento_id)
    elif evaluacion == 0:
        respuesta.validacion = True
        respuesta.save()
        return redirect('planteamientos:inbox', planteamiento)
    else:
        anterior_respuesta = respuesta.respuesta
        respuesta.delete()
        return inbox(request, planteamiento, anterior_respuesta, show='show')
