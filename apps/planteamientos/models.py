from django.db import models
from apps.unidades.models import UnidadOrganizativa, SeccionSindical
from django.utils import timezone
from datetime import datetime, timedelta


def dias_habiles(date: datetime, cont=0):
    if cont == 10:
        return date
    else:
        return dias_habiles(date + timedelta(1), cont + 1 if date.isoweekday() not in [6, 7] else cont)


class Procesos(models.Model):
    proceso = models.CharField(max_length=50)

    def __str__(self):
        return self.proceso


class Planteamiento(models.Model):
    """
    model Planteamientos; \n
     your instance gets: \n
        * titulo -- titulo como referencia \n
        * descripcion -- contendo del planteamiento \n
        * estado -- estado del planteamiento, por defecto "Nuevo" \n
        * fecha -- fecha de creacion \n
        * secretario -- secretario que encomendo el planteamiento \n
        * seccion_sindical -- seccion sindical al que pertenece el secretario
        * unidad -- unidad que recibe el planteamiento
    """

    # estados de los

    ESTANCADO = 'Estancado'
    NUEVO = 'Nuevo'
    PENDIENTE = 'Pendiente'
    SOLUCIONADO = 'Solucionado'

    Choices = (
        (ESTANCADO, 'Estancado'),
        (NUEVO, 'Nuevo'),
        (PENDIENTE, 'Pendiente'),
        (SOLUCIONADO, 'Solucionado')
    )

    # clasificacion de los planteamientos
    Choices2 = (
        ('Territorial', 'Territorial'),
        ('Nacional', 'Nacional')
    )

    titulo = models.CharField(max_length=24)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=Choices, default=ESTANCADO)
    fecha = models.DateField(default=timezone.now)
    modificado = models.DateField(default=timezone.now)
    fecha_vencida = models.DateField()
    secretario = models.CharField(max_length=60)
    seccion_sindical = models.ForeignKey(SeccionSindical, on_delete=models.SET_NULL, null=True)
    unidad = models.ForeignKey(UnidadOrganizativa, on_delete=models.SET_NULL, null=True)
    clasificacion = models.CharField(max_length=12, choices=Choices2, default='Territorial')
    procesos = models.ForeignKey(Procesos, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.titulo}, {self.unidad}, {self.seccion_sindical}, {self.estado}, {self.fecha} "

    def abreviar(self):
        breve = self.descripcion[:100]
        return breve

    def get_unidad(self):
        return self.unidad.nombre

    def tiene_respuestas(self):
        from apps.respuestas.models import HistorialRespuesta
        return any(self.id is i.planteamiento_id for i in HistorialRespuesta.objects.all())
