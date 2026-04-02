from decimal import Decimal, InvalidOperation

from django import forms
from django.db.models import Sum

from choferes.models import Conduce

from .models import AvanceChofer, Pago


class AvanceChoferAdminForm(forms.ModelForm):
    class Meta:
        model = AvanceChofer
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["galones"].label = "Cantidad de galones"
        self.fields["precio_por_galon"].label = "Precio por galon (RD$)"
        self.fields["monto"].label = "Monto total (RD$)"
        self.fields["monto"].required = False
        self.fields["monto"].widget = forms.NumberInput(
            attrs={
                "class": "vDecimalField",
                "step": "0.01",
                "min": "0.00",
                "readonly": "readonly",
            }
        )
        self.fields["monto"].help_text = "Se calcula automaticamente: galones x precio por galon."

    def clean(self):
        cleaned_data = super().clean()
        galones = self._to_decimal(cleaned_data.get("galones"))
        precio_por_galon = self._to_decimal(cleaned_data.get("precio_por_galon"))
        cleaned_data["monto"] = galones * precio_por_galon
        return cleaned_data

    def _to_decimal(self, raw_value):
        if raw_value in (None, ""):
            return Decimal("0.00")
        try:
            return Decimal(str(raw_value).replace(",", ""))
        except (InvalidOperation, TypeError):
            return Decimal("0.00")


class PagoAdminForm(forms.ModelForm):
    saldo_combustible_pendiente = forms.DecimalField(
        label="Saldo pendiente por combustible suministrado por adelantado (RD$)",
        required=False,
        disabled=True,
        decimal_places=2,
        max_digits=12,
        initial=Decimal("0.00"),
    )
    descontar_suministro_combustible = forms.BooleanField(
        label="Desea descontar saldo pendiente por combustible suministrado por adelantado",
        required=False,
    )
    monto_a_cobrar_combustible = forms.DecimalField(
        label="Cantidad a cobrar por combustible (RD$)",
        required=False,
        decimal_places=2,
        max_digits=12,
        initial=Decimal("0.00"),
        widget=forms.NumberInput(
            attrs={"class": "vDecimalField", "step": "0.01", "min": "0.00"}
        ),
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
        exclude = ("conduce",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["monto"].label = "Monto a pagar (RD$)"
        self.fields["metodo"].label = "Metodo de pago"
        self.fields["conduces"].label = "Conduces del pago"
        self.fields["numero_cheque"].label = "Numero del cheque"
        self.fields["numero_recibo_pago"].label = "Numero de recibo de pago"
        self.fields["conduces"].required = False
        self.fields["conduces"].widget = forms.SelectMultiple(
            attrs={"class": "site-input", "size": "10"}
        )
        self.fields["conduces"].help_text = (
            "Selecciona uno o varios conduces para este pago (ejemplo: 10 conduces). "
            "Si falta uno, puedes agregarlo al momento con el boton 'Agregar conduce ahora'."
        )
        self._configurar_queryset_conduces()
        self.fields["numero_cheque"].help_text = "Este campo se usa solo cuando el metodo es cheque."
        self.fields["numero_recibo_pago"].help_text = "Referencia interna del recibo de pago."
        saldo = self._saldo_pendiente_actual()
        self.fields["saldo_combustible_pendiente"].initial = saldo
        self.fields["descontar_suministro_combustible"].initial = saldo > 0

        monto_actual = self._monto_actual()
        aplicar_descuento = self._descontar_avance_actual()
        cobro_actual = self._cobro_combustible_actual()
        if cobro_actual <= 0 and saldo > 0 and aplicar_descuento:
            cobro_actual = min(monto_actual, saldo)
        descuento_estimado = (
            min(cobro_actual, monto_actual, saldo) if aplicar_descuento else Decimal("0.00")
        )
        self.fields["monto_a_cobrar_combustible"].initial = descuento_estimado
        monto_neto = monto_actual - descuento_estimado
        self.fields["monto_neto_a_pagar"].initial = max(monto_neto, Decimal("0.00"))

        if self.instance and self.instance.pk:
            self.fields["descontar_suministro_combustible"].disabled = True
            self.fields["monto_a_cobrar_combustible"].disabled = True
            self.fields["descontar_suministro_combustible"].help_text = (
                "Este control aplica solo al registrar un nuevo pago."
            )
            return

        if saldo <= 0:
            self.fields["descontar_suministro_combustible"].disabled = True
            self.fields["monto_a_cobrar_combustible"].disabled = True
            self.fields["descontar_suministro_combustible"].help_text = (
                "Este chofer no tiene saldo pendiente por combustible suministrado por adelantado."
            )
        else:
            self.fields["descontar_suministro_combustible"].help_text = (
                "Puedes cobrar la deuda en cuotas indicando el monto a descontar."
            )
            self.fields["monto_a_cobrar_combustible"].help_text = (
                "No puede ser mayor al saldo pendiente ni al monto del pago."
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

    def _configurar_queryset_conduces(self):
        chofer_id = self._chofer_id_actual()
        if chofer_id:
            queryset = Conduce.objects.filter(chofer_id=chofer_id).order_by("-fecha", "-id")
        elif self.instance and self.instance.pk:
            queryset = self.instance.conduces.all().order_by("-fecha", "-id")
        else:
            queryset = Conduce.objects.none()
        self.fields["conduces"].queryset = queryset

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
            value = self.data.get("descontar_suministro_combustible")
            return value in (True, "True", "true", "1", 1, "on")
        return bool(self.fields["descontar_suministro_combustible"].initial)

    def _cobro_combustible_actual(self):
        if self.is_bound:
            return self._to_decimal(self.data.get("monto_a_cobrar_combustible"))
        if self.instance and self.instance.pk:
            return self.instance.descuento_avances or Decimal("0.00")
        return self._to_decimal(self.initial.get("monto_a_cobrar_combustible"))

    def clean(self):
        cleaned_data = super().clean()
        aplicar = cleaned_data.get("descontar_suministro_combustible")
        metodo = cleaned_data.get("metodo")
        numero_cheque = (cleaned_data.get("numero_cheque") or "").strip()
        numero_recibo_pago = (cleaned_data.get("numero_recibo_pago") or "").strip()
        chofer = cleaned_data.get("chofer")
        conduces = cleaned_data.get("conduces")
        monto_pago = self._to_decimal(cleaned_data.get("monto"))
        saldo = self._saldo_pendiente_actual()
        monto_cobro = self._to_decimal(cleaned_data.get("monto_a_cobrar_combustible"))

        if aplicar:
            if monto_cobro <= 0:
                self.add_error(
                    "monto_a_cobrar_combustible",
                    "Indica la cantidad que deseas cobrar por combustible.",
                )
            if monto_cobro > saldo:
                self.add_error(
                    "monto_a_cobrar_combustible",
                    "No puedes cobrar mas del saldo pendiente de combustible.",
                )
            if monto_cobro > monto_pago:
                self.add_error(
                    "monto_a_cobrar_combustible",
                    "No puedes cobrar mas del monto del pago.",
                )
        else:
            cleaned_data["monto_a_cobrar_combustible"] = Decimal("0.00")

        if metodo != Pago.Metodo.CHEQUE:
            cleaned_data["numero_cheque"] = ""
        else:
            cleaned_data["numero_cheque"] = numero_cheque

        cleaned_data["numero_recibo_pago"] = numero_recibo_pago

        if chofer and conduces:
            conduces_invalidos = [conduce.numero for conduce in conduces if conduce.chofer_id != chofer.id]
            if conduces_invalidos:
                self.add_error(
                    "conduces",
                    "Todos los conduces seleccionados deben pertenecer al chofer elegido.",
                )

        descuento = (
            min(monto_cobro, saldo, monto_pago) if aplicar and monto_cobro > 0 else Decimal("0.00")
        )
        self.fields["monto_neto_a_pagar"].initial = max(monto_pago - descuento, Decimal("0.00"))
        return cleaned_data
