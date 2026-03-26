from django.contrib import admin

from .forms import ChoferSubcontratistaForm
from .models import Chofer, Conduce


class ConduceInline(admin.TabularInline):
    model = Conduce
    extra = 0


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    form = ChoferSubcontratistaForm
    list_display = (
        "nombre",
        "cedula",
        "licencia",
        "carta_buena_conducta",
        "rntt",
    )
    search_fields = ("nombre", "cedula", "licencia")
    fieldsets = (
        (
            "Identificacion",
            {
                "fields": (
                    "nombres",
                    "apellidos",
                    "cedula",
                    "licencia",
                    "carta_buena_conducta",
                    "rntt",
                )
            },
        ),
    )
    inlines = [ConduceInline]


@admin.register(Conduce)
class ConduceAdmin(admin.ModelAdmin):
    list_display = ("numero", "chofer", "vehiculo", "fecha", "monto_generado", "estado")
    search_fields = ("numero", "chofer__nombre", "vehiculo__placa", "origen", "destino")
