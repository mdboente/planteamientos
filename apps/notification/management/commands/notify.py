from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from apps.planteamientos.models import Planteamiento
from django.utils import timezone
from apps.notification.emails import send_mail, test_connect_email
from apps.unidades.models import UnidadOrganizativa
from config.settings import EMAIL_HOST
from django.contrib.auth.models import User
from apps.respuestas.models import RespuestaTemporal


class Command(BaseCommand):
    help = "Envia un correo a cada representante " \
           "de unidad que le hayan enviado un planteamiento " \
           "en el transcurso del dia "

    def handle(self, *args, **options):
        fecha_hoy = timezone.now().date()
        planteamientos = Planteamiento.objects.filter(Q(fecha=fecha_hoy))
        unidades = UnidadOrganizativa.objects.all()
        respuestas = RespuestaTemporal.objects.filter(Q(fecha=fecha_hoy))
        contd = len(respuestas)
        cant_planteamientos, dicc_unidades = 0, {}
        admins = User.objects.filter(Q(is_staff=True))
        if not test_connect_email():
            raise CommandError('No se ha podido establecer conexión con el HOST {} '.format(EMAIL_HOST))

        for admin in admins:
            cont = len(planteamientos)
            if cont != 0:
                secciones = []
                for i in planteamientos:
                    if i.seccion_sindical not in secciones: secciones.append(i.seccion_sindical)
                mensaje = 'Hola {} !! \r' \
                          'La aplicación Gestión de Planteamientos ha encontrado un total de {} ' \
                          'planteamiento{} realizados el dia de hoy {} por las secci{} . ' \
                          'Cada responsable de unidad ha sido notificado de sus planteamientos correspondientes' \
                    .format(admin.first_name, cont, 's' if cont > 1 else ' ', fecha_hoy,
                            'ones' if len(secciones) > 1 else 'ón')
                str_secciones = ''
                str_secciones += str_secciones.join('\n' + str(i) + '( {})'
                                                    .format(planteamientos.filter(Q(seccion_sindical=i)).count())
                                                    for i in secciones)
                mensaje += str_secciones
                send_mail('Gestión Planteamiento', mensaje, admin.email)


            if contd != 0:
                mensaje = 'Hola {}!! \r' \
                          'Hoy se le han enviado {} {} para ser evaluadas.'\
                    .format(admin.first_name, contd, 'respuesta' if cant_planteamientos == 1 else 'respuestas')
                send_mail('Gestión Planteamiento', mensaje, admin.email)


        for unidad in unidades:
            planteamiento = planteamientos.filter(Q(unidad=unidad))
            cont = len(planteamiento)
            if cont != 0:
                from apps.mixin.utils import sum_days
                secciones = []
                dicc_unidades[unidad.id] = (str(unidad), str(cont))
                cant_planteamientos += cont
                for i in planteamiento:
                    if i.seccion_sindical not in secciones: secciones.append(i.seccion_sindical)

                mensaje = 'Hola {} !! \r' \
                          'La aplicación Gestión de Planteamientos ha encontrado un total de {} ' \
                          'planteamiento{} realizados el dia de hoy {} por las secci{}. Usted tiene ' \
                          '10 días hábiles para dar respuesta a los mismos, su plazo vence {}' \
                    .format(unidad.responsable.get_full_name(),
                            cont,
                            's' if cant_planteamientos == 1 else ' ',
                            fecha_hoy,
                            'ón' if len(secciones) == 1 else 'ones',
                            sum_days(fecha_hoy))
                str_secciones = ''
                str_secciones += str_secciones.join('\n' + str(i) + '( {}),'
                                                    .format(planteamiento.filter(seccion_sindical=i).count())
                                                    for i in secciones)
                mensaje += str_secciones
                send_mail('Gestión Planteamiento', mensaje, unidad.responsable.email)

        output = ' se ha encontrado {} {} realizados el dia de hoy' \
            .format(cant_planteamientos, 'planteamiento' if cant_planteamientos == 1 else 'planteamientos')
        if contd != 0:
            output += '\n se ha {} {} realizadas el dia de hoy'\
                .format(contd, 'respuesta' if cant_planteamientos == 1 else 'respuestas')

        output_end = ''
        output_end += output_end.join('\n' + i + ' : ' + j for i, j in dicc_unidades.values())

        self.stdout.write(output+output_end)
