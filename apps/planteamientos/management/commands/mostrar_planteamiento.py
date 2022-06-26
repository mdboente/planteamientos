from django.core.management.base import BaseCommand
from apps.planteamientos.models import Planteamiento


class Command(BaseCommand):
    help = 'muestra una tabla con los ultimos 10 planteamientos'

    def handle(self, *args, **options):
        differ_line = lambda parm: 23 - len(str(parm))

        table = '=' * 150 + '\n' + \
                'ID' + ' ' * differ_line('id') + ' | ' + \
                'TITULO' + ' ' * differ_line('titulo') + ' | ' + \
                'FECHA' + ' ' * differ_line('fecha') + ' | ' + \
                'SECCION' + ' ' * differ_line('seccion') + ' | ' + \
                'UNIDAD' + ' ' * differ_line('unidad') + ' | ' + \
                'ESTADO' + ' ' * differ_line('estado') + \
                '\n' + '=' * 150

        for planteamiento in Planteamiento.objects.all().order_by('-id')[:10]:
            col_0 = str(planteamiento.id) + ' ' * differ_line(planteamiento.id)
            col_1 = str(planteamiento.titulo) + ' ' * differ_line(planteamiento.titulo)
            col_2 = str(planteamiento.fecha) + ' ' * differ_line(planteamiento.fecha)
            col_3 = str(planteamiento.seccion_sindical.nombre) + ' ' * differ_line(
                planteamiento.seccion_sindical.nombre)
            col_4 = str(planteamiento.unidad.nombre) + ' ' * differ_line(planteamiento.unidad.nombre)
            col_5 = str(planteamiento.estado) + ' ' * differ_line(planteamiento.estado)
            table += '\n' + \
                     col_0 + ' | ' + col_1 + ' | ' + col_2 + ' | ' + col_3 + ' | ' + col_4 + ' | ' + col_5 \
                     + '\n' + '-' * 150
        self.stdout.write(table)
