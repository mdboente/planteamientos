from django.core.management.base import BaseCommand, CommandError
from apps.planteamientos.models import Planteamiento


class Command(BaseCommand):
    help = 'elimina un planteamiento por su id'

    def add_arguments(self, parser):
        parser.add_argument('planteamiento_id', type=int)

    def handle(self, *args, **options):
        planteamiento_id = options['planteamiento_id']
        try:
            planteamiento = Planteamiento.objects.get(id=planteamiento_id)
            planteamiento.delete()
        except Planteamiento.DoesNotExist:
            msj = 'no se ha encontrado un planteamiento con el id {} '.format(planteamiento_id)
            raise CommandError(msj)
        else:
            msj = 'se ha eliminado el Planteamiento {} de {} con éxito'\
                .format(planteamiento.titulo, planteamiento.seccion_sindical)
            self.stdout.write(msj)
