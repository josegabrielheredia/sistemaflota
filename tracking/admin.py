from django.contrib import admin

from .models import Contenedor, Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "marca", "modelo", "estado", "cliente_actual", "fecha_retorno_estimada")
    list_filter = ("estado", "tipo", "marca")
    search_fields = ("placa", "codigo_interno", "marca", "modelo", "cliente_actual")


@admin.register(Contenedor)
class ContenedorAdmin(admin.ModelAdmin):
    list_display = ("codigo", "tipo", "estado", "cliente_actual", "fecha_retorno_estimada")
    list_filter = ("estado", "tipo")
    search_fields = ("codigo", "tipo", "cliente_actual")
