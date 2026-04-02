from decimal import Decimal

from django.contrib import admin
from django.db.models import Sum
from django.http import JsonResponse
from django.urls import path

from choferes.models import Conduce

from .forms import AvanceChoferAdminForm, PagoAdminForm
from .models import AvanceChofer, Pago


@admin.register(AvanceChofer)
class AvanceChoferAdmin(admin.ModelAdmin):
    form = AvanceChoferAdminForm
    list_display = (
        "chofer",
        "fecha",
        "galones",
        "precio_por_galon_rd",
        "monto_rd",
        "saldo_pendiente_rd",
        "estado",
    )
    list_filter = ("estado", "fecha")
    search_fields = ("chofer__nombre", "chofer__cedula", "referencia")

    fieldsets = (
        (
            "Suministro de combustible",
            {"fields": ("chofer", "fecha", "galones", "precio_por_galon", "monto")},
        ),
        (
            "Control de saldo",
            {"fields": ("saldo_pendiente", "estado", "referencia", "observaciones")},
        ),
    )
    readonly_fields = ("saldo_pendiente", "estado")

    class Media:
        js = ("admin/js/avance_combustible_admin.js",)

    @admin.display(description="Monto")
    def monto_rd(self, obj):
        return f"RD$ {obj.monto:,.2f}"

    @admin.display(description="Precio/galon")
    def precio_por_galon_rd(self, obj):
        return f"RD$ {obj.precio_por_galon:,.2f}"

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
        "conduces_resumen",
        "monto_rd",
        "descuento_avances_rd",
        "monto_neto_rd",
        "liquido_avances",
        "metodo",
        "numero_cheque",
        "numero_recibo_pago",
        "fecha",
    )
    list_filter = ("metodo", "fecha", "liquido_avances")
    search_fields = (
        "chofer__nombre",
        "conduce__numero",
        "conduces__numero",
        "referencia",
        "numero_cheque",
        "numero_recibo_pago",
    )
    class Media:
        js = ("admin/js/pagos_avance_admin.js",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("chofer", "conduce").prefetch_related("conduces")

    @admin.display(description="Monto")
    def monto_rd(self, obj):
        return f"RD$ {obj.monto:,.2f}"

    @admin.display(description="Conduces")
    def conduces_resumen(self, obj):
        resumen = obj.resumen_conduces()
        return resumen or "Sin conduce vinculado"

    @admin.display(description="Cobro de combustible suministrado por adelantado")
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
                "saldo-combustible/<int:chofer_id>/",
                self.admin_site.admin_view(self.saldo_avance_view),
                name="pagos_pago_saldo_avance",
            ),
            path(
                "conduces-chofer/<int:chofer_id>/",
                self.admin_site.admin_view(self.conduces_chofer_view),
                name="pagos_pago_conduces_chofer",
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

    def conduces_chofer_view(self, request, chofer_id):
        conduces = (
            Conduce.objects.filter(chofer_id=chofer_id)
            .order_by("-fecha", "-id")
            .values("id", "numero", "fecha", "destino")
        )
        return JsonResponse(
            {
                "conduces": [
                    {
                        "id": item["id"],
                        "texto": f'{item["numero"]} - {item["fecha"].strftime("%d/%m/%Y")} - {item["destino"] or "Sin destino"}',
                    }
                    for item in conduces
                ]
            }
        )

    def save_model(self, request, obj, form, change):
        if not obj.registrado_por_id and request.user.is_authenticated:
            obj.registrado_por = request.user

        aplicar_descuento = (
            not change and form.cleaned_data.get("descontar_suministro_combustible", False)
        )
        monto_a_cobrar = (
            form.cleaned_data.get("monto_a_cobrar_combustible", Decimal("0.00"))
            if not change
            else Decimal("0.00")
        )
        super().save_model(request, obj, form, change)

        if aplicar_descuento and obj.chofer_id and monto_a_cobrar > 0:
            descuento_aplicado = self._aplicar_descuento_combustible(
                chofer_id=obj.chofer_id,
                monto_cobrar=monto_a_cobrar,
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

    def _aplicar_descuento_combustible(self, chofer_id, monto_cobrar):
        monto_restante = monto_cobrar or Decimal("0.00")
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
