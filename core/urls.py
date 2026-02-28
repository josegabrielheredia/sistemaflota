from django.contrib import admin
from django.urls import include, path

from .views import dashboard

admin.site.site_header = "MI SISTEMA FLOTA"
admin.site.site_title = "Panel administrativo"
admin.site.index_title = "Centro de administracion"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("inventario/", include("inventario.urls")),
    path("choferes/", include("choferes.urls")),
    path("pagos/", include("pagos.urls")),
    path("cuentas/", include("cuentas.urls")),
    path("recursos_humanos/", include("recursos_humanos.urls")),
    path("reportes/", include("reportes.urls")),
    path("tracking/", include("tracking.urls")),
    path("", dashboard, name="dashboard"),
]
