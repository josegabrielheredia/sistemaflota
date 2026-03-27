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
        "monto_neto_rd",
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

    @admin.display(description="Neto pagado")
    def monto_neto_rd(self, obj):
        neto = (obj.monto or Decimal("0.00")) - (obj.descuento_avances or Decimal("0.00"))
        if neto < 0:
            neto = Decimal("0.00")
        return f"RD$ {neto:,.2f}"

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

        aplicar_descuento = (
            not change and form.cleaned_data.get("descontar_avance_pendiente", False)
        )
        super().save_model(request, obj, form, change)

        if aplicar_descuento and obj.chofer_id and obj.monto > 0:
            descuento_aplicado = self._aplicar_descuento_avances(
                chofer_id=obj.chofer_id,
                monto_pago=obj.monto,
            )
            if descuento_aplicado > 0:
                saldo_restante = (
                    AvanceChofer.objects.filter(
                        chofer_id=obj.chofer_id,
                        estado=AvanceChofer.Estado.PENDIENTE,
                        saldo_pendiente__gt=0,
                    ).aggregate(total=Sum("saldo_pendiente"))["total"]
                    or Decimal("0.00")
                )
                obj.descuento_avances = descuento_aplicado
                obj.liquido_avances = saldo_restante <= 0
                obj.save(update_fields=["descuento_avances", "liquido_avances"])

    def _aplicar_descuento_avances(self, chofer_id, monto_pago):
        monto_restante = monto_pago or Decimal("0.00")
        if monto_restante <= 0:
            return Decimal("0.00")

        total_descontado = Decimal("0.00")
        avances = AvanceChofer.objects.filter(
            chofer_id=chofer_id,
            estado=AvanceChofer.Estado.PENDIENTE,
            saldo_pendiente__gt=0,
        ).order_by("fecha", "id")

        for avance in avances:
            if monto_restante <= 0:
                break

            saldo = avance.saldo_pendiente or Decimal("0.00")
            if saldo <= 0:
                continue

            descuento = min(saldo, monto_restante)
            nuevo_saldo = saldo - descuento
            avance.saldo_pendiente = nuevo_saldo
            avance.estado = (
                AvanceChofer.Estado.LIQUIDADO
                if nuevo_saldo <= 0
                else AvanceChofer.Estado.PENDIENTE
            )
            avance.save(update_fields=["saldo_pendiente", "estado"])

            total_descontado += descuento
            monto_restante -= descuento

        return total_descontado
