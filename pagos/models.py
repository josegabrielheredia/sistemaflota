from django.conf import settings
from django.db import models


class Pago(models.Model):
    class Metodo(models.TextChoices):
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
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    metodo = models.CharField(max_length=20, choices=Metodo.choices)
    referencia = models.CharField(max_length=100, blank=True)
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

    def __str__(self):
        return f"{self.chofer.nombre} - {self.monto}"
