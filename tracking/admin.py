from django.contrib import admin

from .models import Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "marca", "modelo", "estado", "cliente_actual", "fecha_retorno_estimada")
    search_fields = ("placa", "codigo_interno", "marca", "modelo", "cliente_actual")
