from decimal import Decimal

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
    liquidar_avances_pendientes = forms.BooleanField(
        label="Marcar avances pendientes como pagados",
        required=False,
    )

    class Meta:
        model = Pago
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        saldo = self._saldo_pendiente_actual()
        self.fields["saldo_avance_pendiente"].initial = saldo

        if saldo <= 0:
            self.fields["liquidar_avances_pendientes"].disabled = True
            self.fields["liquidar_avances_pendientes"].help_text = (
                "Este chofer no tiene avances pendientes."
            )
        else:
            self.fields["liquidar_avances_pendientes"].help_text = (
                "Si marcas esta opcion, los avances pendientes del chofer se cerraran."
            )

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
