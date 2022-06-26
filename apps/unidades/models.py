from django.db import models
from django.contrib.auth.models import User


class UnidadOrganizativa(models.Model):
    """
     model Unidad Organizativas; \n
     your instance gets: \n
        *  nombre -- Oranizational Unit name \n
        *  responsable -- responsible user for the Organizational Unit

    """

    nombre = models.CharField(max_length=60, unique=True)
    responsable = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre

    def delete(self, **kwargs):
        from apps.planteamientos.models import Planteamiento
        planteamientos = Planteamiento.objects.filter(unidad_id=self.id)
        for i in planteamientos:
            i.unidad_id = 'unidad'
            i.save()
        super(UnidadOrganizativa, self).delete(**kwargs)




class SeccionSindical(models.Model):
    """
     model SeccionSindical; \n
     your instance gets: \n
        * nombre -- Seccion Sindical name \n
        * secretario -- name of secretary \n
        * unidad -- relationship with the unit

    """

    nombre = models.CharField(max_length=60, unique=True)
    secretario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    unidad = models.ForeignKey(UnidadOrganizativa, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.nombre