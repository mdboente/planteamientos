from django.db.models import Q, QuerySet
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from apps.mixin.login import secretario
from .models import Planteamiento, Procesos
from apps.mixin.utils import UsuarioLogin, Html, sum_days
from apps.mixin.forms import FormPlanteamiento
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from apps.respuestas.models import HistorialRespuesta
from apps.notification.notification import Notification
from apps.notification.emails import send_mail
from django.contrib import messages
from apps.unidades.models import UnidadOrganizativa, SeccionSindical
from django.views import View
from xlsxwriter import Workbook
import  io
from django.http import HttpResponse
import datetime


class ImportXLXSService:

    @classmethod
    def write_header(cls, workbook, worksheet):
        header = ["Fecha de Creación", "Fecha de Vencimiento",
                  "Clasificación", "Proceso", "Unidad", "Sección Sindical",
                  "Secretario", "Título", "Descripción", "Respuesta"]

        header_format = workbook.add_format({"bold": True})
        header_format.set_bg_color("00b0f0")
        worksheet.write_row("A1", header, header_format)
        worksheet.set_column(0, 7, 20)
        worksheet.set_column(8, 11, 30)

        return worksheet

    @classmethod
    def execute(cls, planteamientos):
        file = io.BytesIO()

        workbook = Workbook(file)
        worksheet = workbook.add_worksheet()

        cls.write_header(workbook, worksheet)

        row = 2
        for planteamiento in planteamientos:
            worksheet.write(f"A{row}", planteamiento.fecha.isoformat())

            worksheet.write(f"B{row}", planteamiento.fecha_vencida.isoformat())

            worksheet.write(f"C{row}", planteamiento.clasificacion)

            worksheet.write(f"D{row}", planteamiento.procesos.proceso)

            worksheet.write(f"E{row}", planteamiento.unidad
                            and planteamiento.unidad.nombre or "")

            worksheet.write(f"F{row}",
                            planteamiento.seccion_sindical
                            and planteamiento.seccion_sindical.nombre or "")

            worksheet.write(f"G{row}", planteamiento.secretario)
            worksheet.write(f"H{row}", planteamiento.titulo)
            worksheet.write(f"I{row}", planteamiento.descripcion)

            respuesta = HistorialRespuesta.objects.filter(
                planteamiento_id=planteamiento.id)\
                .values("descripcion").first()

            worksheet.write(f"J{row}", respuesta and
                            respuesta.get("descripcion", ""))

            row += 1

        workbook.set_properties({
            'title': 'Planteamientos',
            'subject': 'Planteamientos',
            'author': 'user',
            'manager': 'manager',
            'company': 'ETECSA S.A',
            'category': 'Example spreadsheets',
            'keywords': 'Sample, Example, Properties',
            'created': datetime.date(2018, 1, 1)})

        workbook.close()
        file.seek(0)

        return file


class PlanteamientosImportXLSXService(View):

    def get(self, request):

        planteamientos = Planteamiento.objects.all()
        file = ImportXLXSService.execute(planteamientos)

        filename = "planteamientos.xlsx"

        response = HttpResponse(
            file,
            content_type="application/vnd.openxmlformats-"
                         "officedocument.spreadsheetml.sheet"
        )

        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response

@login_required(login_url="login")
def planteamiento(request, todos) -> HttpResponse:
    usuario = UsuarioLogin(request)
    planteamientos = usuario.plant()
    unidades = UnidadOrganizativa.objects.all()
    secciones = SeccionSindical.objects.all()
    procesos = Procesos.objects.all()
    fecha_hoy = timezone.now().date()

    if todos == 1:
        planteamientos = Planteamiento.objects.all()
    if todos == 2:
        usuario = UsuarioLogin(request)
        planteamientos = usuario.plant(estado=None)

    if request.method == 'POST':
        fields = ['titulo', 'estado', 'seccion_sindical_id',
                  'unidad_id', 'clasificacion', 'procesos_id',
                  'fecha', 'fecha_vencida']

        fields = [{i: request.POST[i]} for i in request.POST
                  if request.POST[i] not in ('No Especificado', '') and i in fields]
        for field in fields:
            resp = planteamientos.filter(**field)
            planteamientos = resp

    return render(request, 'planteamientos/planteamientos.html', locals())


@login_required(login_url="login")
def inbox(request, planteamiento_id, respuesta_a_editar=" ", *, show='hidden') -> HttpResponse:
    procesos = Procesos.objects.all()
    usuario = UsuarioLogin(request)
    planteamientos = usuario.plant(limit=10)
    notify = Notification(request)
    notification = notify.get_list_notify()

    if planteamiento_id != 0:
        mostrar = get_object_or_404(Planteamiento, id=planteamiento_id)
        respuestas = HistorialRespuesta.objects.filter(Q(planteamiento_id=mostrar.id))

        for i in respuestas:
            try:
                if i.planteamiento.seccion_sindical.secretario.id == request.user.id:
                    i.leido = True
                    i.save()

            except AttributeError:
                pass
    else:
        mostrar = usuario.ultimo_planteamiento()
        respuestas = usuario.respuestas()

    form = FormPlanteamiento(initial={'unidad': mostrar.unidad,
                                      'procesos': mostrar.procesos} if mostrar is not None else None)
    if mostrar is not None:
        if mostrar.estado != 'Solucionado':
            atraso = (mostrar.fecha_vencida - timezone.now().date()).days
            if 0 < atraso < 5:
                msj = 'Este planteamiento le quedan {} días para que ' \
                      'culmine su plazo de respuesta'.format(atraso)
                messages.warning(request, msj, 'ADVERTENCIA !!')
            elif atraso <= 0 and not mostrar.tiene_respuestas():
                historial = HistorialRespuesta()
                respuesta = 'Se incumple el tiempo de respuesta del planteamiento por %s ' \
                            % ('el Área Rectora Nacional' if mostrar.clasificacion == 'Nacional'
                               else 'la Actividad Rectora Territorial')
                historial.planteamiento_id = mostrar.id
                historial.descripcion = respuesta
                historial.fecha = timezone.now().date()
                historial.autor = 'Gestión Planteamiento'
                mostrar.estado = 'Pendiente'
                mostrar.save()
                historial.save()

    if respuestas is not None: respuestas = respuestas.order_by('-id')
    if request.method == 'GET':
        if 'hidden' in request.GET.values():
            show = 'show'

    if request.method == "POST":
        if 'clasificar' in request.POST:
            mostrar.clasificacion = request.POST['clasificacion']
            mostrar.save()
        elif 'proceso' in request.POST:
            mostrar.procesos_id = request.POST['procesos']
            mostrar.save()
        else:
            mostrar.unidad_id = request.POST['unidad']
            mostrar.fecha = timezone.now().date()
            mostrar.fecha_vencida = sum_days(timezone.now().date())
            mostrar.save()

            # enviar correo
            mensaje = 'Hola {}!! \r' \
                      'Se le ha reenviado por el administrador {}' \
                      ' un Planteamiento de la sección sindical {}, ' \
                      'Tiene plazo de 10 días hábiles para darle respuesta.' \
                .format(mostrar.unidad.responsable.first_name, request.user.first_name,
                        mostrar.seccion_sindical.nombre)
            send_mail('Gestión Planteamiento', mensaje, mostrar.unidad.responsable.email)

            # notificar
            mensaje2 = 'Se ha reenviado el planteamiento de la sección {} para la unidad {}' \
                .format(mostrar.seccion_sindical.nombre, mostrar.unidad)
            messages.success(request, mensaje2, 'ÉXITOS !')

    Notification.del_notify(request, planteamiento_id)

    return render(request, 'planteamientos/inbox.html', locals())


@user_passes_test(secretario, login_url='login')
@login_required(login_url="login")
def crear_planteamiento(request) -> HttpResponse:
    form = FormPlanteamiento()

    if request.method == "POST":
        datos = {key: request.POST[key] for key in request.POST}
        descripcion = Html.get_text(datos['descripcion'])
        datos['descripcion'] = descripcion
        datos['secretario'] = request.user.first_name
        datos['seccion_sindical'] = UsuarioLogin.relacion(request, seccion=True)
        form = FormPlanteamiento(data=datos)
        if form.is_valid():
            form.save()
            # notificar
            mensaje = 'Se ha adicionado satisfactoriamente el planteamiento {}'.format(datos['titulo'])
            messages.success(request, mensaje, 'ÉXITO ! ')
            return redirect('planteamientos:planteamiento', 0)
        else:
            # notificar
            mensaje = 'Ha cometido un error completando los campos del formulario Planteamiento'
            messages.error(request, mensaje, 'ERROR ! ')
    return render(request, 'planteamientos/crear.html', {'form': form})


def editar_planteamiento(request, id_planteamiento):
    p = get_object_or_404(Planteamiento, id=id_planteamiento)
    form = FormPlanteamiento(initial={'unidad': p.unidad, 'procesos': p.procesos, 'titulo': p.titulo})
    descripcion = p.descripcion
    if request.method == "POST":
        datos = {key: request.POST[key] for key in request.POST}
        descripcion = Html.get_text(datos['descripcion'])
        datos['descripcion'] = descripcion
        datos['secretario'] = p.secretario
        datos['seccion_sindical'] = p.seccion_sindical
        form = FormPlanteamiento(data=datos, instance=p)
        if form.is_valid():
            form.save()
            mensaje = 'Se ha editado el planteamiento {} correctamente'.format(datos['titulo'])
            messages.success(request, mensaje, 'ÉXITO ! ')
            return redirect('planteamientos:inbox', id_planteamiento)

    return render(request, 'planteamientos/crear.html', locals())


@login_required(login_url="login")
def notificaciones(request):
    notify = Notification(request)
    lista_notificaciones = notify.get_list_notify()
    return render(request, 'planteamientos/notification.html', locals())


class PlanteamientosAprobar(View):

    def get(self, request, planteamiento_id, aprobado):

        planteamiento = Planteamiento.objects.get(id=planteamiento_id)

        approach_approve_input_dto = ApproachApproveInputDTO(
            approach=planteamiento,
            approve=bool(aprobado),
            authenticatd_user=request.user.get_full_name(),
            authenticatd_user_email=request.user.email
        )

        planteamiento_aprobado = ApproachApproveService.execute(
            approach_approve_input_dto)

        if not planteamiento_aprobado.is_approved:
            planteamiento = Planteamiento.objects.filter(
                seccion_sindical__id=planteamiento.seccion_sindical.id)\
                .last()

        return inbox(request, planteamiento.id)


@dataclass
class ApproachApproveOutputDTO:
    """ ApproachApproveInputDTO class """
    approach: Planteamiento
    is_approved: bool
    estado: str


@dataclass
class ApproachApproveInputDTO:
    """ ApproachApproveInputDTO class """
    authenticatd_user_email: str
    authenticatd_user: str
    approach: Planteamiento
    approve: bool = False



class ApproachApproveService:
    """ ApproachApproveService class """

    @classmethod
    def execute(cls, approach_approve_dto: ApproachApproveInputDTO):

        approach = approach_approve_dto.approach
        approve = approach_approve_dto.approve

        if approve:
            approach.estado = Planteamiento.NUEVO
            approach.modificado = timezone.now()

            enables_days_to_expire = 10
            expiration_date = sum_days(
                approach.modificado, enables_days_to_expire)
            approach.fecha_vencida = expiration_date

            approach.save()
        else:
            secretary = approach.seccion_sindical.secretario
            template = get_template('emails/desaprobar_planteamiento.html')
            context = {
                'user': secretary.get_full_name(),
                'approach': approach.titulo,
                'created_date': approach.fecha,
                'authenticated_user': approach_approve_dto.authenticatd_user,
                'authenticated_user_email':
                    approach_approve_dto.authenticatd_user_email,
                'description': approach.descripcion
            }

            message = template.render(context)
            subject = "Gestión Planteamientos"

            send_mail(subject, message, secretary.email)

            approach.delete()

        return ApproachApproveOutputDTO(approach, approve, approach.estado)
