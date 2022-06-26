from django.contrib import admin
from django.urls import path, include
from apps.mixin import login, errors
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import cache_control
from django.conf import settings

handler404 = errors.handler_404
handler500 = errors.handler_500


urlpatterns = [
    path('admin/', admin.site.urls),
    path('planteamientos/', include('apps.planteamientos.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
    path('unidades/', include('apps.respuestas.urls')),
    path('unidades/', include('apps.unidades.urls')),
    path('', login.login, name='login'),
    path('logout', login.logout, name='logout'),
    path('olvidado/', login.olvidar_contrasegna, name='olvidar')

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, view=cache_control(no_cache=True, must_revalidate=True)(serve))
