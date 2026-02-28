from django.db import models


class Vehiculo(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        ALQUILADO = "alquilado", "Alquilado"
        MANTENIMIENTO = "mantenimiento", "Mantenimiento"
        FUERA_SERVICIO = "fuera_servicio", "Fuera de servicio"

    placa = models.CharField(max_length=20, unique=True)
    codigo_interno = models.CharField(max_length=30, blank=True)
    marca = models.CharField(max_length=80, blank=True)
    modelo = models.CharField(max_length=80)
    anio = models.PositiveIntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=60, blank=True)
    capacidad = models.CharField(max_length=60, blank=True)
    color = models.CharField(max_length=30, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
    )
    ultima_ubicacion = models.CharField(max_length=200, blank=True)
    cliente_actual = models.CharField(max_length=150, blank=True)
    fecha_salida = models.DateField(null=True, blank=True)
    fecha_retorno_estimada = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ("placa",)

    def __str__(self):
        return self.placa


class Contenedor(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        ALQUILADO = "alquilado", "Alquilado"
        MANTENIMIENTO = "mantenimiento", "Mantenimiento"
        FUERA_SERVICIO = "fuera_servicio", "Fuera de servicio"

    codigo = models.CharField(max_length=40, unique=True)
    tipo = models.CharField(max_length=80)
    capacidad = models.CharField(max_length=60, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
    )
    ubicacion_actual = models.CharField(max_length=200, blank=True)
    cliente_actual = models.CharField(max_length=150, blank=True)
    fecha_salida = models.DateField(null=True, blank=True)
    fecha_retorno_estimada = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Contenedor"
        verbose_name_plural = "Contenedores"
        ordering = ("codigo",)

    def __str__(self):
        return self.codigo
