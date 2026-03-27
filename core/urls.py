from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

admin.site.site_header = "Transporte Victorino Diroche, S.R.L."
admin.site.site_title = "Panel administrativo"
admin.site.index_title = "Centro de administracion"
admin.site.site_url = None


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        RedirectView.as_view(url="/admin/login/?next=/admin/", permanent=False),
        name="home",
    ),
]
