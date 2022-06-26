from django.db import models
from apps.planteamientos.models import Planteamiento
from apps.unidades.models import SeccionSindical
from django.utils import timezone


# Create your models here.


class RespuestaTemporal(models.Model):
    """

    model RespuestaTemporal; \n
    your instance gets: \n
        * respuesta -- content of the temporal response \n
        * fecha -- date of response \n
        * validacion -- validation, this is a way of see if the manager saw this response,
                    True if are read, and False if not is it.
        * planteamiento -- approach related to this response

    """
    respuesta = models.TextField()
    fecha = models.DateField(default=timezone.now)
    validacion = models.BooleanField(default=False)
    planteamiento = models.OneToOneField(Planteamiento, on_delete=models.SET_NULL, null=True)
    autor = models.CharField(max_length=10)


class HistorialRespuesta(models.Model):
    """
    model HistorialRespuesta; \n
    your instance gets: \n
        * description -- the description of de answer \n
        * aprobacion -- secretary approval, is True if they agree, or False if not is it \n
        * leido -- return a boolen value, is True if the answer is read, or False if not is it. \n
        * fecha -- date of the answer \n
        * planteamientos -- relationship with the approach

    """

    descripcion = models.TextField()
    aprobacion = models.BooleanField(default=False)
    leido = models.BooleanField(default=False)
    fecha = models.DateField()
    planteamiento = models.ForeignKey(Planteamiento, on_delete=models.SET_NULL, null=True)
    autor = models.CharField(max_length=100)

