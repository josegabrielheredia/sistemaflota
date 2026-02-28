from django.contrib import admin

from .models import Reporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "fecha")
    list_filter = ("categoria", "fecha")
    search_fields = ("titulo", "descripcion")
