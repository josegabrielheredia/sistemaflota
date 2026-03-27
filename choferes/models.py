from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class Chofer(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"
        SUSPENDIDO = "suspendido", "Suspendido"

    class MetodoPago(models.TextChoices):
        CHEQUE = "cheque", "Cheque"
        TRANSFERENCIA = "transferencia", "Transferencia"

    nombre = models.CharField(max_length=150)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    licencia = models.CharField(max_length=50)
    carta_buena_conducta = models.BooleanField(default=False)
    rntt = models.BooleanField(default=False)
    categoria_licencia = models.CharField(max_length=50, blank=True)
    vencimiento_licencia = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    metodo_pago_preferido = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
        blank=True,
    )
    banco = models.CharField(max_length=100, blank=True)
    titular_cuenta = models.CharField(max_length=150, blank=True)
    numero_cuenta = models.CharField(max_length=50, blank=True)
    honorario_referencial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_registro = models.DateField(default=timezone.localdate, editable=False)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Chofer subcontratista"
        verbose_name_plural = "Choferes subcontratistas"
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre


class Conduce(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = "borrador", "Borrador"
        LIQUIDADO = "liquidado", "Liquidado"
        PAGADO = "pagado", "Pagado"

    numero = models.CharField(max_length=30, unique=True)
    chofer = models.ForeignKey(
        Chofer,
        on_delete=models.CASCADE,
        related_name="conduces",
    )
    vehiculo = models.ForeignKey(
        "tracking.Vehiculo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conduces",
    )
    fecha = models.DateField()
    origen = models.CharField(max_length=150, blank=True)
    destino = models.CharField(max_length=150, blank=True)
    descripcion = models.TextField(blank=True)
    monto_generado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.BORRADOR,
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Conduce"
        verbose_name_plural = "Conduces"
        ordering = ("-fecha", "-id")

    def clean(self):
        super().clean()
        numero_normalizado = (self.numero or "").strip().upper()
        if not numero_normalizado:
            return

        self.numero = numero_normalizado
        duplicado = Conduce.objects.filter(numero__iexact=numero_normalizado)
        if self.pk:
            duplicado = duplicado.exclude(pk=self.pk)
        if duplicado.exists():
            raise ValidationError(
                {"numero": "Ya existe un conduce registrado con este numero."}
            )

    def save(self, *args, **kwargs):
        if self.numero:
            self.numero = self.numero.strip().upper()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.numero
