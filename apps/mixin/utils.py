import datetime
from abc import ABC
from copy import copy

from django.db.models import Q
from apps.planteamientos.models import *
from apps.respuestas.models import HistorialRespuesta
from html.parser import HTMLParser


class UsuarioLogin(object):
    """
    Realiza un breve atajo a algunos elementos
     de la aplicacion scp del proyecto a traves del usuario:
    \n
    funciones --> [ is_seccion , is_unit , approaches , ] \n
    """

    def __init__(self, request: object, *, unidad: object = None, seccion: object = None):
        self.user = request.user
        self.unidad = unidad
        self.seccion = seccion
        if hasattr(self.user, 'seccionsindical'):
            self.seccion = self.user.seccionsindical
        if hasattr(self.user, 'unidadorganizativa'):
            self.unidad = self.user.unidadorganizativa

    @property
    def tiene_seccion(self):
        """
        Relacion del objeto con una seccion sindical.
        :return: True si el objeto pertenece a una seccion sindical,
        False si no lo es, ...
        """

        if self.seccion is not None:
            return True
        else:
            return False

    @property
    def tiene_unidad(self) -> bool:
        """
        Relacion del objeto con una unidad organizativa.
        @return: True si el objeto pertenece a una unidad organizativa,
        False si no lo es, ...
        """
        if self.unidad is not None:
            return True
        else:
            return False

    @property
    def no_tiene_relacion(self):
        unidad = self.tiene_unidad
        seccion = self.tiene_seccion
        admin = self.user.is_staff
        none = not unidad and not seccion and not admin
        return True if none else False

    @classmethod
    def relacion(cls, request, *, seccion: bool = None, unidad: bool = None):
        obj = cls(request)
        if obj.tiene_seccion and seccion is True:
            return obj.get_seccion(pk=True)
        elif obj.tiene_unidad and unidad is True:
            return obj.get_unidad(pk=True)

    def plant(self, *, limit: object = None, estado: object = "Nuevo") -> list:
        """
        devuelve una lista de todos los planteamientos a los q esta asociado el objeto.
        :param limit: especifica un limite de los ultimos planteamientos
        :return: una lista de planteamientos asociados al objeto
        @rtype: object
        """

        q_conditions = Q()

        if self.tiene_seccion and not self.user.is_superuser:
            q_conditions &= Q(seccion_sindical_id=self.seccion.id)
        elif self.tiene_unidad:
            q_conditions &= Q(unidad_id=self.unidad.id)
            q_conditions &= ~Q(estado=Planteamiento.ESTANCADO)

        plant = Planteamiento.objects.filter(q_conditions).order_by("-id")

        if limit is not None:
            plant = plant[:limit]
        return plant

    def por_ciento(self):
        planteamientos = self.plant(estado=None)
        estados = ("Nuevo", "Pendiente", "Solucionado")
        if len(planteamientos) != 0:
            return {i: (len(self.plant(estado=i)) / len(planteamientos)) * 100 for i in estados}

    def respuestas(self) -> list:
        """
        todas las respuestas asignadas al ultimo Planteamiento
        :rtype: list
        """
        planteamiento = self.ultimo_planteamiento()

        if planteamiento is not None:
            respuestas = HistorialRespuesta.objects.filter(Q(planteamiento_id=planteamiento.id))
            for i in respuestas:
                if i.planteamiento.seccion_sindical.secretario.id == self.user.id:
                    i.leido = True
                    i.save()
            return respuestas

    def ultimo_planteamiento(self):
        """
        el ultimo planteamiento realacionado al usuario..
        :return: el ultimo planteamiento
        """
        planteamiento = self.plant()

        if len(planteamiento) == 0:
            return None
        else:
            return planteamiento[0]

    @property
    def cant_plant(self):
        cont = len(self.plant())
        return cont

    @property
    def mas_un_planteamiento(self):
        if self.cant_plant != 0:
            return True

    @property
    def notificaciones(self):
        planteamientos = self.plant()
        if len(planteamientos) == 0:
            return []
        else:
            plant = planteamientos.filter(Q(estado='Nuevo'))
            return plant[:4]

    def get_seccion(self, pk=True):
        resp = self.seccion.id
        if pk is False:
            resp = self.seccion
        return resp

    def get_unidad(self, pk=True):
        resp = self.unidad.id
        if pk is False:
            resp = self.unidad
        return resp

    def vinculo(self):
        if self.user.is_superuser:
            return {'vinculo': "Administrador", "unidad": 'Administrador'}
        if self.user.is_staff:
            return {'vinculo': "Supervisor", "unidad": self.get_unidad(pk=False)
                    if self.tiene_unidad else 'Supervisor'}
        elif self.tiene_seccion:
            return {'vinculo': "Secretario", "unidad": self.get_seccion(pk=False)}
        elif self.tiene_unidad:
            return {'vinculo': "Responsable", "unidad": self.get_unidad(pk=False)}
        else:
            return {'vinculo': 'No se han encontrado vinculos', "unidad": "Ninguna"}


class Html(HTMLParser, ABC):

    def __init__(self, *args, **kwargs):
        self.text = ''
        super().__init__(*args, **kwargs)

    @staticmethod
    def is_html(tag):
        resp = False
        if '<' and '>' in tag:
            resp = True
        return resp

    def handle_starttag(self, tag, attrs):
        if tag != 'span' and tag != 'div':
            self.text += '\r'
        if tag == 'li':
            self.text += '* '

    def handle_data(self, data):
        self.text += data

    def handle_entityref(self, name):
        if name == 'nbsp;':
            self.text += '  '

    @classmethod
    def get_text(cls, text):
        f = cls()
        f.feed(text)
        return f.text


def sum_days(date: datetime, n_days: int):
    """ Get date after n enables days  """

    count = 0
    while count < n_days:
        date = date + timedelta(days=1)
        if date.isoweekday() not in [6, 7]:
            count += 1

    return date
