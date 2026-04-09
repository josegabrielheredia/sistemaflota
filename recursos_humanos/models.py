from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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
    apellidos = models.CharField(max_length=150, blank=True)
    cedula = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
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
        return f"{self.nombre} {self.apellidos}".strip()


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
    pagada_sin_disfrute = models.BooleanField(
        default=False,
        verbose_name="Pagada sin disfrute",
        help_text="Indica si las vacaciones fueron pagadas sin disfrute de dias.",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PROGRAMADA,
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Vacaci\u00f3n"
        verbose_name_plural = "Vacaciones"
        ordering = ("-fecha_inicio",)

    def clean(self):
        super().clean()
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError(
                {"fecha_fin": "La fecha final no puede ser menor que la fecha de inicio."}
            )

    def estado_actual(self, fecha_referencia=None):
        fecha_referencia = fecha_referencia or timezone.localdate()
        if fecha_referencia < self.fecha_inicio:
            return self.Estado.PROGRAMADA
        if self.fecha_inicio <= fecha_referencia <= self.fecha_fin:
            return self.Estado.EN_CURSO
        return self.Estado.COMPLETADA

    @classmethod
    def sincronizar_estados(cls):
        hoy = timezone.localdate()
        cls.objects.filter(fecha_inicio__gt=hoy).exclude(estado=cls.Estado.PROGRAMADA).update(
            estado=cls.Estado.PROGRAMADA
        )
        cls.objects.filter(
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
        ).exclude(estado=cls.Estado.EN_CURSO).update(estado=cls.Estado.EN_CURSO)
        cls.objects.filter(fecha_fin__lt=hoy).exclude(estado=cls.Estado.COMPLETADA).update(
            estado=cls.Estado.COMPLETADA
        )

    def save(self, *args, **kwargs):
        self.estado = self.estado_actual()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.empleado.nombre} - {self.fecha_inicio}"


class Capacitacion(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="capacitaciones",
    )
    tema = models.CharField(max_length=150)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    costo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Costo de la capacitacion, si aplica.",
    )
    proveedor = models.CharField(max_length=150, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Capacitaci\u00f3n"
        verbose_name_plural = "Capacitaciones"
        ordering = ("-fecha_inicio",)

    def clean(self):
        super().clean()
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError(
                {"fecha_fin": "La fecha final no puede ser menor que la fecha de inicio."}
            )
        if self.costo is not None and self.costo <= 0:
            raise ValidationError({"costo": "El costo debe ser mayor que cero si es indicado."})

    def __str__(self):
        return f"{self.tema} - {self.empleado.nombre}"


class PagoEmpleado(models.Model):
    class Metodo(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        CHEQUE = "cheque", "Cheque"
        TRANSFERENCIA = "transferencia", "Transferencia"

    class Quincena(models.TextChoices):
        PRIMERA = "primera", "Primera quincena"
        SEGUNDA = "segunda", "Segunda quincena"

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="pagos",
    )
    fecha = models.DateField()
    quincena = models.CharField(
        max_length=10,
        choices=Quincena.choices,
        default=Quincena.PRIMERA,
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=Metodo.choices)
    referencia = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Pago de empleado"
        verbose_name_plural = "Pagos de empleados"
        ordering = ("-fecha", "-id")

    @staticmethod
    def quincena_desde_fecha(fecha):
        if not fecha:
            return PagoEmpleado.Quincena.PRIMERA
        return (
            PagoEmpleado.Quincena.PRIMERA
            if fecha.day <= 15
            else PagoEmpleado.Quincena.SEGUNDA
        )

    def save(self, *args, **kwargs):
        if not self.quincena:
            self.quincena = self.quincena_desde_fecha(self.fecha)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.empleado} - {self.monto}"


class RegistroGasto(models.Model):
    fecha = models.DateField(default=timezone.localdate)
    con_comprobante = models.BooleanField(default=False)
    numero_comprobante = models.CharField(max_length=80, blank=True)
    proveedor = models.CharField(max_length=150)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    itbis = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    propinas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    motivo = models.CharField(max_length=255)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Registro de gasto"
        verbose_name_plural = "Registros de gastos"
        ordering = ("-fecha", "-id")

    def clean(self):
        super().clean()
        errors = {}

        if self.con_comprobante and not (self.numero_comprobante or "").strip():
            errors["numero_comprobante"] = (
                "Debes indicar el numero de comprobante cuando el gasto es con comprobante."
            )

        if self.valor is not None and self.valor <= 0:
            errors["valor"] = "El valor del gasto debe ser mayor que cero."
        if self.itbis is not None and self.itbis < 0:
            errors["itbis"] = "El ITBIS no puede ser negativo."
        if self.propinas is not None and self.propinas < 0:
            errors["propinas"] = "Las propinas no pueden ser negativas."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.con_comprobante:
            self.numero_comprobante = ""
        self.numero_comprobante = (self.numero_comprobante or "").strip()
        return super().save(*args, **kwargs)

    @property
    def total(self):
        return (self.valor or 0) + (self.itbis or 0) + (self.propinas or 0)

    def __str__(self):
        return f"{self.fecha:%d/%m/%Y} - {self.proveedor} - RD$ {self.total:,.2f}"
