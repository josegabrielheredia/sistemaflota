from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AvanceChofer(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        LIQUIDADO = "liquidado", "Liquidado"

    chofer = models.ForeignKey(
        "choferes.Chofer",
        on_delete=models.CASCADE,
        related_name="avances",
    )
    fecha = models.DateField(default=timezone.localdate)
    galones = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_por_galon = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    referencia = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="avances_chofer_registrados",
    )

    class Meta:
        verbose_name = "Suministro de combustible a chofer"
        verbose_name_plural = "Suministros de combustible a choferes"
        ordering = ("-fecha", "-id")

    def clean(self):
        super().clean()
        errors = {}

        if self.galones is None or self.galones <= 0:
            errors["galones"] = "La cantidad de galones debe ser mayor que cero."
        if self.precio_por_galon is None or self.precio_por_galon <= 0:
            errors["precio_por_galon"] = "El precio por galon debe ser mayor que cero."

        if errors:
            raise ValidationError(errors)

        self.monto = (self.galones or 0) * (self.precio_por_galon or 0)

        saldo = self.saldo_pendiente
        if saldo is None:
            return
        if saldo < 0:
            raise ValidationError({"saldo_pendiente": "El saldo pendiente no puede ser negativo."})
        if self.monto is not None and saldo > self.monto:
            raise ValidationError({"saldo_pendiente": "El saldo pendiente no puede superar el monto del suministro."})

    def save(self, *args, **kwargs):
        self.monto = (self.galones or 0) * (self.precio_por_galon or 0)
        if self.saldo_pendiente is None:
            self.saldo_pendiente = self.monto
        self.estado = self.Estado.LIQUIDADO if self.saldo_pendiente <= 0 else self.Estado.PENDIENTE
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.chofer.nombre} - {self.galones} gal - RD$ {self.monto:,.2f}"


class Pago(models.Model):
    class Metodo(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        CHEQUE = "cheque", "Cheque"
        TRANSFERENCIA = "transferencia", "Transferencia"

    chofer = models.ForeignKey(
        "choferes.Chofer",
        on_delete=models.CASCADE,
        related_name="pagos",
    )
    conduce = models.ForeignKey(
        "choferes.Conduce",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos",
    )
    conduces = models.ManyToManyField(
        "choferes.Conduce",
        blank=True,
        related_name="pagos_multiples",
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    metodo = models.CharField(max_length=20, choices=Metodo.choices)
    numero_cheque = models.CharField(max_length=50, blank=True)
    numero_recibo_pago = models.CharField(max_length=50, blank=True)
    referencia = models.CharField(max_length=100, blank=True)
    descuento_avances = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    liquido_avances = models.BooleanField(default=False, editable=False)
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pagos_registrados",
    )

    class Meta:
        verbose_name = "Pago a chofer"
        verbose_name_plural = "Pagos a choferes"
        ordering = ("-fecha", "-id")

    def clean(self):
        super().clean()
        if self.metodo == self.Metodo.CHEQUE and not (self.numero_cheque or "").strip():
            raise ValidationError(
                {"numero_cheque": "Debes indicar el numero del cheque para este metodo de pago."}
            )

    def save(self, *args, **kwargs):
        if self.metodo != self.Metodo.CHEQUE:
            self.numero_cheque = ""
        self.numero_cheque = (self.numero_cheque or "").strip()
        self.numero_recibo_pago = (self.numero_recibo_pago or "").strip()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.chofer.nombre} - RD$ {self.monto:,.2f}"

    def resumen_conduces(self):
        numeros = list(self.conduces.values_list("numero", flat=True))
        if numeros:
            return ", ".join(numeros)
        if self.conduce:
            return self.conduce.numero
        return ""
