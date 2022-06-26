from apps.mixin.utils import UsuarioLogin
from apps.planteamientos.models import Planteamiento
from django.db.models import Q
from django.http import HttpRequest


class Notification(UsuarioLogin):

    def __init__(self, request: object):
        super().__init__(request)

    @staticmethod
    def session(notification: list, asunto='') -> dict:

        """ construir la estructura de datos que vamos
        a manejar en plantilla y enviar a la session """

        notify = [{'id': i.id,
                   'titulo': i.titulo,
                   'fecha': str(i.fecha),
                   'remitente': str(i.unidad.responsable.username),
                   'asunto': asunto}
                  for i in notification]

        return {'notify': notify[:5], 'cant_notify': len(notify)}

    def plant_con_respuestas(self, unidad=False) -> list:

        """ Filtrado de Planteamientos que no han sido leidos aun y relacionados a un usuario
         si unidad es True se filtra con respecto a esa unidad, y si es False se filtra por la seccion sindical """

        planteamientos = Planteamiento.objects.filter(Q(historialrespuesta__leido=False))
        if unidad:
            planteamientos = planteamientos.filter(Q(unidad__responsable_id=self.user.id))
        else:
            planteamientos = planteamientos.filter(Q(seccion_sindical__secretario_id=self.user.id))
        return list(planteamientos)

    def plant_recientes(self, admin=False) -> list:

        """ Filtrado de los Planteamientos nuevos que estan relacionados a un usuario,
         si admin es True se buscan todos los planteamientos de lo contrario se
         filtran por la unidad perteneciente al usuario """

        planteamientos = Planteamiento.objects.all()
        if not admin: planteamientos = planteamientos.filter(Q(unidad__responsable_id=self.user.id))
        recientes = [i for i in planteamientos if i.estado == 'Nuevo']
        return list(recientes)

    def resp_desaprobadas(self):
        return list(Planteamiento.objects.filter(Q(unidad__responsable_id=self.user.id) &
                                                 Q(respuestatemporal__validacion=True)))

    @property
    def resp_recientes(self) -> list:

        """ Una propieda del objeto de filtrar todos los
        planteamientos que tiene una respuesta temporal """

        planteamientos = [i for i in Planteamiento.objects.all() if hasattr(i, 'respuestatemporal')]
        return list(planteamientos)

    def create_notify(self):
        """ Una Funcion que analiza el roll del objeto y lo redirecciona
        de acuerdo a las notificaciones que requiere """

        if self.user.is_staff:
            return self.roll_admin()
        elif self.tiene_seccion:
            return self.roll_seccion()
        elif self.tiene_unidad:
            return self.roll_unidad()
        else:
            return {'notify': [], 'cant_notify': 0}

    @classmethod
    def del_notify(cls, request: HttpRequest, plateamiento_id: int):

        """ Un metodo de la clase Notification que pide como parametro un objeto HttpRequest,
         y el id de un Planteamiento, y analiza la estructura de datos una vez contruida en la funcion session y
            elimina la notificacion perteneciente al id pasado como parametro"""

        session = request.session.get('notification', [])
        new_notify = []
        try:
            for n in session['notify']:
                if n['id'] != plateamiento_id:
                    new_notify.append(n)
        except KeyError:
            pass

        session['notify'] = new_notify
        session['cant_notify'] = len(new_notify)
        request.session.modified = True

    @classmethod
    def notify(cls, request: HttpRequest):
        """ Un Metodo de la clase que toma como parametro un objeto HttpRequest
        en introduce un diccionario en la propiedad request.session de la clase HttpRequest """

        obj = cls(request)
        resp = obj.create_notify()
        request.session['notification'] = resp

    def roll_unidad(self, get_list=False):
        """ Roll preteneciente a una representante de unidad """
        resp_desaprobada = self.resp_desaprobadas()
        if get_list: return resp_desaprobada
        return self.session(resp_desaprobada, asunto='corregir')

    def roll_admin(self, get_list=False):
        """ Roll perteneciente a un administrador """
        resp_reciente = self.resp_recientes
        if get_list: return resp_reciente
        return self.session(resp_reciente, asunto='evaluar')

    def roll_seccion(self, get_list=False):
        """ Roll perteneciente a un secretario de una seccion """
        con_respuesta = self.plant_con_respuestas()
        if get_list: return con_respuesta
        return self.session(con_respuesta, asunto='respondido')

    def get_list_notify(self):
        if self.user.is_staff:
            return self.roll_admin(get_list=True)
        elif self.tiene_seccion:
            return self.roll_seccion(get_list=True)
        elif self.tiene_unidad:
            return self.roll_unidad(get_list=True)
        else:
            return []

    @classmethod
    def refresh(cls, request: object, notify: list):
        request.session['notification']['notify'] = notify
        request.session['notification']['cant_notify'] = len(notify)




