from django.shortcuts import render, redirect
from django.db.models import Q
from apps.mixin.forms import *
from django.shortcuts import get_object_or_404
from django.contrib import messages


# --------------------------  funciones del modulo unidad organizativa  ---------------------------- #


def listar(request):
    unidades = UnidadOrganizativa.objects.all()
    form = FormUnidad()
    if request.method == "GET":
        x = request.GET.get('buscar', '')
        unidades = unidades.filter(Q(responsable__first_name__icontains=x) | Q(nombre__icontains=x))
    elif request.method == "POST":
        form = FormUnidad(data=request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            msj = '{} se le ha asignado la unidad {}'.format(f.responsable.get_full_name(), f.nombre)
            messages.success(request, msj, 'ÉXITOS !! ')
            f.save()
        else:
            msj = 'Usted ha cometido un error en los campos, '
            messages.error(request, msj.join(i + ', ' for i in form.errors))

    return render(request, 'unidades/unidad_organizativa.html', locals())


def editar(request):
    if request.method == "POST":
        unidad = get_object_or_404(UnidadOrganizativa, id=request.POST["Editar"])
        unidad.nombre = request.POST["nombre"]
        unidad.responsable_id = int(request.POST["responsable"])
        unidad.save()
        messages.success(request, 'Se ha editado la unidad %s satisfactoriamente' % unidad.nombre, 'ÉXITOS !!')
    return redirect("unidades:listar")


def eliminar(request, unidad_id):
    unidad = UnidadOrganizativa.objects.get(id=unidad_id)
    p = Planteamiento.objects.filter(unidad=unidad).count()
    unidad.delete()
    messages.success(request, 'Se ha eliminado la unidad %s' % unidad.nombre, 'ÉXITOS !!')
    if p > 0: messages.warning(request,
                               '{} planteamientos ya no guardan relación con la Unidad Organizativa eliminada'.format(p),
                               'ADVERTENCIA !! ')
    return redirect('unidades:listar')


# --------------------------  funciones del modulo seccion sindical  ---------------------------- #


def listar_seccion(request):
    secciones = SeccionSindical.objects.all()
    form = FormSeccion()
    if request.method == "GET":
        x = request.GET.get('buscar', '')
        secciones = secciones.filter(Q(secretario__first_name__icontains=x) | Q(nombre__icontains=x))
    elif request.method == "POST":
        form = FormSeccion(data=request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            msj = '{} se le ha asignado la sección {}'.format(f.secretario.get_full_name(), f.nombre)
            messages.success(request, msj, 'ÉXITOS !! ')
            f.save()
        else:
            msj = 'Usted ha cometido un error en los campos, '
            messages.error(request, msj.join(i + ', ' for i in form.errors))

    return render(request, 'unidades/seccion_sindical.html', locals())


def editar_seccion(request):
    if request.method == "POST":
        seccion = get_object_or_404(SeccionSindical, id=request.POST["Editar"])
        seccion.nombre = request.POST["nombre"]
        seccion.secretario_id = int(request.POST["secretario"])
        seccion.unidad_id = int(request.POST["unidad"])
        seccion.save()
        messages.success(request, 'Se ha ediado la unidad %s satisfactoriamente' % seccion.nombre, 'ÉXITOS !!')
    return redirect("unidades:listar_seccion")


def eliminar_seccion(request, seccion_id):
    seccion = SeccionSindical.objects.get(id=seccion_id)
    p = Planteamiento.objects.filter(seccion_sindical=seccion).count()
    seccion.delete()
    messages.success(request, 'Se ha eliminado la sección %s' % seccion.nombre, 'EXITOS !!')
    if p > 0: messages.warning(request,
                               '{} planteamientos ya no guardan relación con la Sección Sindical eliminada'.format(p),
                               'ADVERTENCIA !! ')
    return redirect("unidades:listar_seccion")
