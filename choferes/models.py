from django.db import models


class Chofer(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"
        SUSPENDIDO = "suspendido", "Suspendido"

    nombre = models.CharField(max_length=150)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    licencia = models.CharField(max_length=50)
    categoria_licencia = models.CharField(max_length=50, blank=True)
    vencimiento_licencia = models.DateField(null=True, blank=True)
    empleado = models.OneToOneField(
        "recursos_humanos.Empleado",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="perfil_chofer",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Chofer"
        verbose_name_plural = "Choferes"
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

    def __str__(self):
        return self.numero
