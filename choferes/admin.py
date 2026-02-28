from django.contrib import admin

from .models import Chofer, Conduce


class ConduceInline(admin.TabularInline):
    model = Conduce
    extra = 0


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cedula", "licencia", "categoria_licencia", "estado")
    list_filter = ("estado", "categoria_licencia")
    search_fields = ("nombre", "cedula", "licencia", "telefono")
    inlines = [ConduceInline]


@admin.register(Conduce)
class ConduceAdmin(admin.ModelAdmin):
    list_display = ("numero", "chofer", "vehiculo", "fecha", "monto_generado", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("numero", "chofer__nombre", "vehiculo__placa", "origen", "destino")
