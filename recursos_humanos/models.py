from django.db import models


class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre


class Cargo(models.Model):
    nombre = models.CharField(max_length=100)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        related_name="cargos",
    )
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"
        ordering = ("nombre",)
        unique_together = ("nombre", "departamento")

    def __str__(self):
        return f"{self.nombre} - {self.departamento.nombre}"


class Empleado(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"
        SUSPENDIDO = "suspendido", "Suspendido"

    nombre = models.CharField(max_length=150)
    cedula = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField()
    cargo = models.ForeignKey(
        Cargo,
        on_delete=models.PROTECT,
        related_name="empleados",
    )
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    salario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre


class TipoLicencia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    requiere_aprobacion = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de licencia"
        verbose_name_plural = "Tipos de licencias"
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre


class Licencia(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = "programada", "Programada"
        ACTIVA = "activa", "Activa"
        CERRADA = "cerrada", "Cerrada"
        CANCELADA = "cancelada", "Cancelada"

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="licencias",
    )
    tipo = models.ForeignKey(
        TipoLicencia,
        on_delete=models.PROTECT,
        related_name="licencias",
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.CharField(max_length=255, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PROGRAMADA,
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Licencia"
        verbose_name_plural = "Licencias"
        ordering = ("-fecha_inicio",)

    def __str__(self):
        return f"{self.empleado.nombre} - {self.tipo.nombre}"


class Vacacion(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA = "programada", "Programada"
        EN_CURSO = "en_curso", "En curso"
        COMPLETADA = "completada", "Completada"

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="vacaciones",
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PROGRAMADA,
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Vacación"
        verbose_name_plural = "Vacaciones"
        ordering = ("-fecha_inicio",)

    def __str__(self):
        return f"{self.empleado.nombre} - {self.fecha_inicio}"


class Capacitacion(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="capacitaciones",
    )
    tema = models.CharField(max_length=150)
    fecha = models.DateField()
    proveedor = models.CharField(max_length=150, blank=True)
    horas = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Capacitación"
        verbose_name_plural = "Capacitaciones"
        ordering = ("-fecha",)

    def __str__(self):
        return f"{self.tema} - {self.empleado.nombre}"
