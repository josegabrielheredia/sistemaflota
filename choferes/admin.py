from django.contrib import admin
from django.db.models import Sum

from .forms import ChoferSubcontratistaForm
from .models import Chofer, Conduce
from pagos.models import AvanceChofer


class ConduceInline(admin.TabularInline):
    model = Conduce
    extra = 0


class AvanceChoferInline(admin.TabularInline):
    model = AvanceChofer
    extra = 0
    fields = ("fecha", "monto", "saldo_pendiente", "estado", "referencia")
    readonly_fields = ("saldo_pendiente", "estado")
    show_change_link = True


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    form = ChoferSubcontratistaForm
    list_display = (
        "nombre",
        "cedula",
        "licencia",
        "carta_buena_conducta",
        "rntt",
        "saldo_avance_pendiente",
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
    inlines = [ConduceInline, AvanceChoferInline]

    @admin.display(description="Saldo avance pendiente")
    def saldo_avance_pendiente(self, obj):
        saldo = (
            obj.avances.filter(
                estado=AvanceChofer.Estado.PENDIENTE, saldo_pendiente__gt=0
            ).aggregate(total=Sum("saldo_pendiente"))["total"]
            or 0
        )
        return f"RD$ {saldo:,.2f}"


@admin.register(Conduce)
class ConduceAdmin(admin.ModelAdmin):
    list_display = ("numero", "chofer", "vehiculo", "fecha", "monto_generado", "estado")
    search_fields = ("numero", "chofer__nombre", "vehiculo__placa", "origen", "destino")
