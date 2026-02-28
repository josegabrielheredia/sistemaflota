from django.db import models


class Cuenta(models.Model):
    class Tipo(models.TextChoices):
        PAGAR = "pagar", "Por pagar"
        COBRAR = "cobrar", "Por cobrar"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PARCIAL = "parcial", "Parcial"
        PAGADA = "pagada", "Pagada"
        VENCIDA = "vencida", "Vencida"

    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    categoria = models.CharField(max_length=80, blank=True)
    tercero = models.CharField(max_length=150, blank=True)
    chofer = models.ForeignKey(
        "choferes.Chofer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cuentas",
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"
        ordering = ("fecha_vencimiento", "nombre")

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_display()}"


class AbonoCuenta(models.Model):
    class Metodo(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        CHEQUE = "cheque", "Cheque"
        TRANSFERENCIA = "transferencia", "Transferencia"

    cuenta = models.ForeignKey(
        Cuenta,
        on_delete=models.CASCADE,
        related_name="abonos",
    )
    fecha = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=Metodo.choices)
    referencia = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Abono de cuenta"
        verbose_name_plural = "Abonos de cuenta"
        ordering = ("-fecha", "-id")

    def __str__(self):
        return f"{self.cuenta.nombre} - {self.monto}"
