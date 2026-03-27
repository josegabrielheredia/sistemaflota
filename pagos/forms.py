from decimal import Decimal, InvalidOperation

from django import forms
from django.db.models import Sum

from .models import AvanceChofer, Pago


class PagoAdminForm(forms.ModelForm):
    saldo_avance_pendiente = forms.DecimalField(
        label="Saldo pendiente por avances (RD$)",
        required=False,
        disabled=True,
        decimal_places=2,
        max_digits=12,
        initial=Decimal("0.00"),
    )
    descontar_avance_pendiente = forms.BooleanField(
        label="Desea cobrarle el avance pendiente",
        required=False,
    )
    monto_neto_a_pagar = forms.DecimalField(
        label="Monto neto a pagar (RD$)",
        required=False,
        disabled=True,
        decimal_places=2,
        max_digits=12,
        initial=Decimal("0.00"),
    )

    class Meta:
        model = Pago
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["monto"].label = "Monto a pagar (RD$)"
        saldo = self._saldo_pendiente_actual()
        self.fields["saldo_avance_pendiente"].initial = saldo
        self.fields["descontar_avance_pendiente"].initial = saldo > 0

        monto_actual = self._monto_actual()
        aplicar_descuento = self._descontar_avance_actual()
        descuento_estimado = min(monto_actual, saldo) if aplicar_descuento else Decimal("0.00")
        monto_neto = monto_actual - descuento_estimado
        self.fields["monto_neto_a_pagar"].initial = max(monto_neto, Decimal("0.00"))

        if self.instance and self.instance.pk:
            self.fields["descontar_avance_pendiente"].disabled = True
            self.fields["descontar_avance_pendiente"].help_text = (
                "Este control aplica solo al registrar un nuevo pago."
            )
            return

        if saldo <= 0:
            self.fields["descontar_avance_pendiente"].disabled = True
            self.fields["descontar_avance_pendiente"].help_text = (
                "Este chofer no tiene avances pendientes."
            )
        else:
            self.fields["descontar_avance_pendiente"].help_text = (
                "Si marcas esta opcion, se descuenta del pago hasta cubrir el saldo pendiente."
            )

    def _to_decimal(self, raw_value):
        if raw_value in (None, ""):
            return Decimal("0.00")
        try:
            return Decimal(str(raw_value).replace(",", ""))
        except (InvalidOperation, TypeError):
            return Decimal("0.00")

    def _chofer_id_actual(self):
        if self.is_bound:
            return self.data.get("chofer") or None
        if self.instance and self.instance.pk:
            return self.instance.chofer_id
        initial_chofer = self.initial.get("chofer")
        return getattr(initial_chofer, "pk", initial_chofer)

    def _saldo_pendiente_actual(self):
        chofer_id = self._chofer_id_actual()
        if not chofer_id:
            return Decimal("0.00")
        total = (
            AvanceChofer.objects.filter(
                chofer_id=chofer_id,
                estado=AvanceChofer.Estado.PENDIENTE,
                saldo_pendiente__gt=0,
            ).aggregate(total=Sum("saldo_pendiente"))["total"]
            or Decimal("0.00")
        )
        return total

    def _monto_actual(self):
        if self.is_bound:
            return self._to_decimal(self.data.get("monto"))
        if self.instance and self.instance.pk:
            return self.instance.monto or Decimal("0.00")
        return self._to_decimal(self.initial.get("monto"))

    def _descontar_avance_actual(self):
        if self.is_bound:
            value = self.data.get("descontar_avance_pendiente")
            return value in (True, "True", "true", "1", 1, "on")
        return bool(self.fields["descontar_avance_pendiente"].initial)
