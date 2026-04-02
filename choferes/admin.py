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
    fields = (
        "fecha",
        "galones",
        "precio_por_galon",
        "monto",
        "saldo_pendiente",
        "estado",
        "referencia",
    )
    readonly_fields = ("monto", "saldo_pendiente", "estado")
    show_change_link = True


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    form = ChoferSubcontratistaForm
    list_display = (
        "nombre",
        "cedula",
        "licencia",
        "categoria_licencia",
        "vencimiento_licencia",
        "estado_licencia_actual",
        "carta_buena_conducta",
        "rntt",
        "vencimiento_carnet_rntt",
        "estado_rntt_actual",
        "seguro_ley",
        "vencimiento_seguro_ley",
        "estado_seguro_actual",
        "saldo_combustible_pendiente",
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
                    "categoria_licencia",
                    "vencimiento_licencia",
                    "carta_buena_conducta",
                    "rntt",
                    "vencimiento_carnet_rntt",
                    "seguro_ley",
                    "vencimiento_seguro_ley",
                )
            },
        ),
    )
    inlines = [ConduceInline, AvanceChoferInline]

    @admin.display(description="Saldo pendiente por combustible suministrado por adelantado")
    def saldo_combustible_pendiente(self, obj):
        saldo = (
            obj.avances.filter(
                estado=AvanceChofer.Estado.PENDIENTE, saldo_pendiente__gt=0
            ).aggregate(total=Sum("saldo_pendiente"))["total"]
            or 0
        )
        return f"RD$ {saldo:,.2f}"

    @admin.display(description="Estado licencia")
    def estado_licencia_actual(self, obj):
        return obj.estado_licencia()

    @admin.display(description="Estado carnet RNTT")
    def estado_rntt_actual(self, obj):
        return obj.estado_carnet_rntt()

    @admin.display(description="Estado seguro ley")
    def estado_seguro_actual(self, obj):
        return obj.estado_seguro_ley()


@admin.register(Conduce)
class ConduceAdmin(admin.ModelAdmin):
    list_display = ("numero", "chofer", "vehiculo", "fecha", "monto_generado", "estado")
    search_fields = ("numero", "chofer__nombre", "vehiculo__placa", "origen", "destino")
