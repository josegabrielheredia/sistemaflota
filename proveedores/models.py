from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    fecha_registro = models.DateField(default=timezone.localdate, editable=False)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Empresa proveedora"
        verbose_name_plural = "Empresas proveedoras"
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre


class RegistroProveedor(models.Model):
    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        related_name="registros",
    )
    fecha = models.DateField(default=timezone.localdate)
    placa = models.CharField(max_length=20)
    ruta = models.CharField(max_length=200, help_text="Salida / destino")
    numero_transporte = models.CharField(max_length=50, verbose_name="No. de transporte")
    destino = models.CharField(max_length=120)
    tarifa = models.DecimalField(max_digits=12, decimal_places=2)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Registro operativo de proveedor"
        verbose_name_plural = "Registros operativos de proveedores"
        ordering = ("-fecha", "-id")

    def clean(self):
        super().clean()
        if self.tarifa is not None and self.tarifa <= 0:
            raise ValidationError({"tarifa": "La tarifa debe ser mayor que cero."})

    def __str__(self):
        return f"{self.proveedor.nombre} - {self.placa} - {self.fecha:%d/%m/%Y}"
