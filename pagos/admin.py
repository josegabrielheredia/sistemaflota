from decimal import Decimal

from django.contrib import admin
from django.db.models import Sum
from django.http import JsonResponse
from django.urls import path

from .forms import PagoAdminForm
from .models import AvanceChofer, Pago


@admin.register(AvanceChofer)
class AvanceChoferAdmin(admin.ModelAdmin):
    list_display = ("chofer", "fecha", "monto_rd", "saldo_pendiente_rd", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("chofer__nombre", "chofer__cedula", "referencia")

    @admin.display(description="Monto")
    def monto_rd(self, obj):
        return f"RD$ {obj.monto:,.2f}"

    @admin.display(description="Saldo pendiente")
    def saldo_pendiente_rd(self, obj):
        saldo = obj.saldo_pendiente or 0
        return f"RD$ {saldo:,.2f}"

    def save_model(self, request, obj, form, change):
        if not obj.registrado_por_id and request.user.is_authenticated:
            obj.registrado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    form = PagoAdminForm
    change_form_template = "admin/pagos/pago/change_form.html"
    list_display = (
        "chofer",
        "conduce",
        "monto_rd",
        "descuento_avances_rd",
        "liquido_avances",
        "metodo",
        "fecha",
    )
    list_filter = ("metodo", "fecha", "liquido_avances")
    search_fields = ("chofer__nombre", "conduce__numero", "referencia")

    class Media:
        js = ("admin/js/pagos_avance_admin.js",)

    @admin.display(description="Monto")
    def monto_rd(self, obj):
        return f"RD$ {obj.monto:,.2f}"

    @admin.display(description="Descuento avances")
    def descuento_avances_rd(self, obj):
        return f"RD$ {obj.descuento_avances:,.2f}"

    def get_urls(self):
        custom_urls = [
            path(
                "saldo-avance/<int:chofer_id>/",
                self.admin_site.admin_view(self.saldo_avance_view),
                name="pagos_pago_saldo_avance",
            ),
        ]
        return custom_urls + super().get_urls()

    def saldo_avance_view(self, request, chofer_id):
        saldo = (
            AvanceChofer.objects.filter(
                chofer_id=chofer_id,
                estado=AvanceChofer.Estado.PENDIENTE,
                saldo_pendiente__gt=0,
            ).aggregate(total=Sum("saldo_pendiente"))["total"]
            or Decimal("0.00")
        )
        return JsonResponse(
            {"saldo_pendiente": f"{saldo:.2f}", "tiene_pendiente": saldo > 0}
        )

    def save_model(self, request, obj, form, change):
        if not obj.registrado_por_id and request.user.is_authenticated:
            obj.registrado_por = request.user

        aplicar_liquidacion = (
            not change and form.cleaned_data.get("liquidar_avances_pendientes", False)
        )
        super().save_model(request, obj, form, change)

        if aplicar_liquidacion and obj.chofer_id:
            avances_pendientes = AvanceChofer.objects.filter(
                chofer_id=obj.chofer_id,
                estado=AvanceChofer.Estado.PENDIENTE,
                saldo_pendiente__gt=0,
            )
            total_saldo = (
                avances_pendientes.aggregate(total=Sum("saldo_pendiente"))["total"]
                or Decimal("0.00")
            )
            if total_saldo > 0:
                avances_pendientes.update(
                    saldo_pendiente=Decimal("0.00"),
                    estado=AvanceChofer.Estado.LIQUIDADO,
                )
                obj.descuento_avances = total_saldo
                obj.liquido_avances = True
                obj.save(update_fields=["descuento_avances", "liquido_avances"])
