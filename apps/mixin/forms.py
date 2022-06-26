from django import forms
from django.shortcuts import get_object_or_404

from apps.planteamientos.models import Planteamiento
from apps.unidades.models import *
from django.contrib.auth.models import User


class FormPlanteamiento(forms.ModelForm):
    """ formulario para crear y validar todos los datos de la tabla Planteamientos """

    class Meta:
        model = Planteamiento
        exclude = ['estado', 'fecha', 'clasificacion', 'fecha_vencida']

        widgets = {'unidad': forms.Select(attrs={'class': "select2_single form-control"}),
                   'titulo': forms.TextInput(attrs={'class': "form-control ", 'list': 'listado'}),
                   'procesos': forms.Select(attrs={'class': "select2_single form-control"})
                   }

    def get_planteamientos(self):
        return self.Meta.model.objects.all()


class FormUnidad(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuarios = [(i.id, i.get_full_name()) for i in User.objects.all()
                         if not hasattr(i, 'unidadorganizativa')
                         and not hasattr(i, 'seccionsindical')]
        self.fields['responsable'].choices = self.usuarios

    class Meta:
        model = UnidadOrganizativa
        fields = '__all__'

        widgets = {'nombre': forms.TextInput(attrs={'class': "form-control "}),
                   'responsable': forms.Select(attrs={'class': "form-control"})
                   }

    def get_usuarios(self):
        return [get_object_or_404(User, id=ids) for ids, nombre in self.usuarios]


class FormSeccion(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuarios = [(i.id, i.get_full_name()) for i in User.objects.all()
                         if not hasattr(i, 'seccionsindical')
                         and not hasattr(i, 'unidadorganizativa')]
        self.unidades = UnidadOrganizativa.objects.all()
        self.fields['secretario'].choices = self.usuarios

    class Meta:
        model = SeccionSindical
        fields = '__all__'

        widgets = {'nombre': forms.TextInput(attrs={'class': "form-control "}),
                   'secretario': forms.Select(attrs={'class': "form-control"}),
                   'unidad': forms.Select(attrs={'class': "form-control"})
                   }

    def get_usuarios(self):
        return [get_object_or_404(User, id=ids) for ids, nombre in self.usuarios]
