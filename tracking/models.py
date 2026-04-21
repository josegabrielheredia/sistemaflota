from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


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
    anio = models.PositiveIntegerField("A\u00f1o", null=True, blank=True)
    tipo = models.CharField(max_length=60, blank=True)
    capacidad = models.CharField(max_length=60, blank=True)
    color = models.CharField(max_length=30, blank=True)
    es_propiedad_empresa = models.BooleanField(default=True)
    dueno_nombre = models.CharField(max_length=150, blank=True)
    dueno_documento = models.CharField(max_length=30, blank=True)
    dueno_telefono = models.CharField(max_length=20, blank=True)
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
        verbose_name = "Vehiculo"
        verbose_name_plural = "Vehiculos"
        ordering = ("placa",)

    def clean(self):
        if not self.es_propiedad_empresa and not self.dueno_nombre:
            raise ValidationError(
                {"dueno_nombre": "Indica el nombre del dueno cuando el vehiculo no es de la empresa."}
            )

    def __str__(self):
        return self.placa


class Contenedor(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        ALQUILADO = "alquilado", "Alquilado"

    class Origen(models.TextChoices):
        LOCAL = "local", "Local"
        IMPORTADO = "importado", "Importado"

    class FormaPago(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        TRANSFERENCIA = "transferencia", "Transferencia"
        CHEQUE = "cheque", "Cheque"

    codigo = models.CharField(max_length=40, unique=True, verbose_name="Ficha del contenedor")
    tamano_pies = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tamano (pies)")
    tipo = models.CharField(max_length=80, blank=True)
    capacidad = models.CharField(max_length=60, blank=True)
    color = models.CharField(max_length=30, blank=True)
    local_o_importado = models.CharField(
        max_length=15,
        choices=Origen.choices,
        default=Origen.LOCAL,
        verbose_name="Local o importado",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
    )
    cliente_actual = models.CharField(max_length=150, blank=True, verbose_name="A quien se le alquilo")
    fecha_salida = models.DateField(null=True, blank=True, verbose_name="Fecha de inicio")
    fecha_retorno_estimada = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    costo_alquiler = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Costo del alquiler",
    )
    forma_pago = models.CharField(
        max_length=20,
        choices=FormaPago.choices,
        default=FormaPago.EFECTIVO,
        verbose_name="Forma de pago",
    )
    numero_referencia_pago = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Numero de referencia de pago",
    )
    referido_por = models.CharField(max_length=150, blank=True, verbose_name="Referido por")
    servicio_a = models.CharField(max_length=150, blank=True, verbose_name="A quien se le da el servicio")
    ubicacion_actual = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Contenedor"
        verbose_name_plural = "Contenedores"
        ordering = ("codigo",)

    def clean(self):
        if self.estado == self.Estado.ALQUILADO:
            errors = {}
            if not self.cliente_actual:
                errors["cliente_actual"] = "Indica a quien se le alquilo el contenedor."
            if not self.fecha_salida:
                errors["fecha_salida"] = "Indica la fecha de inicio del alquiler."
            if not self.fecha_retorno_estimada:
                errors["fecha_retorno_estimada"] = "Indica la fecha de fin del alquiler."
            if errors:
                raise ValidationError(errors)

        if self.forma_pago in (self.FormaPago.TRANSFERENCIA, self.FormaPago.CHEQUE):
            if not (self.numero_referencia_pago or "").strip():
                raise ValidationError(
                    {
                        "numero_referencia_pago": "Indica el numero de referencia de pago."
                    }
                )

        if (
            self.fecha_salida
            and self.fecha_retorno_estimada
            and self.fecha_salida > self.fecha_retorno_estimada
        ):
            raise ValidationError(
                {
                    "fecha_retorno_estimada": "La fecha de fin no puede ser menor que la fecha de inicio."
                }
            )

    def save(self, *args, **kwargs):
        if self.forma_pago == self.FormaPago.EFECTIVO:
            self.numero_referencia_pago = ""
        self.numero_referencia_pago = (self.numero_referencia_pago or "").strip()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo


class Chasis(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        ALQUILADO = "alquilado", "Alquilado"

    codigo = models.CharField(max_length=40, unique=True, verbose_name="Ficha del chasis")
    tamano_pies = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tamano (pies)")
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
    )
    ubicacion_actual = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Chasis"
        verbose_name_plural = "Chasis"
        ordering = ("codigo",)

    def __str__(self):
        return self.codigo


class AlquilerContenedor(models.Model):
    class FormaPago(models.TextChoices):
        EFECTIVO = "efectivo", "Efectivo"
        TRANSFERENCIA = "transferencia", "Transferencia"
        CHEQUE = "cheque", "Cheque"

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        CERRADO = "cerrado", "Cerrado"

    contenedor = models.ForeignKey(
        Contenedor,
        on_delete=models.PROTECT,
        related_name="alquileres",
        verbose_name="Contenedor",
    )
    con_chasis = models.BooleanField(default=False, verbose_name="Con chasis")
    chasis = models.ForeignKey(
        Chasis,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="alquileres",
        verbose_name="Chasis",
    )
    cliente = models.CharField(max_length=150, verbose_name="A quien se le da el servicio")
    referido_por = models.CharField(max_length=150, blank=True, verbose_name="Referido por")
    numero_contacto_referencia = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Numero de contacto de referencia",
    )
    numero_contrato_compromiso = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Numero de contrato de compromiso",
    )
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha de fin")
    costo_alquiler = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Costo del alquiler",
    )
    forma_pago = models.CharField(
        max_length=20,
        choices=FormaPago.choices,
        default=FormaPago.EFECTIVO,
        verbose_name="Forma de pago",
    )
    numero_referencia_pago = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Numero de referencia de pago",
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Alquiler de contenedor"
        verbose_name_plural = "Alquileres de contenedores"
        ordering = ("-fecha_inicio", "-id")

    def clean(self):
        errors = {}
        if self.con_chasis and not self.chasis:
            errors["chasis"] = "Selecciona el chasis cuando el alquiler es con chasis."
        if not self.con_chasis:
            self.chasis = None

        if self.forma_pago in (self.FormaPago.TRANSFERENCIA, self.FormaPago.CHEQUE):
            if not (self.numero_referencia_pago or "").strip():
                errors["numero_referencia_pago"] = "Indica el numero de referencia de pago."

        if self.fecha_fin and self.fecha_inicio and self.fecha_fin < self.fecha_inicio:
            errors["fecha_fin"] = "La fecha de fin no puede ser menor que la fecha de inicio."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.forma_pago == self.FormaPago.EFECTIVO:
            self.numero_referencia_pago = ""
        self.numero_referencia_pago = (self.numero_referencia_pago or "").strip()
        super().save(*args, **kwargs)
        self._sync_estado_operativo()

    def delete(self, *args, **kwargs):
        contenedor_id = self.contenedor_id
        chasis_id = self.chasis_id
        super().delete(*args, **kwargs)
        if contenedor_id:
            Contenedor.objects.filter(pk=contenedor_id).update(estado=Contenedor.Estado.DISPONIBLE)
        if chasis_id:
            Chasis.objects.filter(pk=chasis_id).update(estado=Chasis.Estado.DISPONIBLE)

    def _sync_estado_operativo(self):
        contenedor_estado = (
            Contenedor.Estado.ALQUILADO if self.estado == self.Estado.ACTIVO else Contenedor.Estado.DISPONIBLE
        )
        Contenedor.objects.filter(pk=self.contenedor_id).update(estado=contenedor_estado)

        if self.con_chasis and self.chasis_id:
            chasis_estado = (
                Chasis.Estado.ALQUILADO if self.estado == self.Estado.ACTIVO else Chasis.Estado.DISPONIBLE
            )
            Chasis.objects.filter(pk=self.chasis_id).update(estado=chasis_estado)
        elif self.chasis_id:
            Chasis.objects.filter(pk=self.chasis_id).update(estado=Chasis.Estado.DISPONIBLE)

    def __str__(self):
        return f"{self.contenedor.codigo} - {self.fecha_inicio:%d/%m/%Y}"


class ReciboContenedor(models.Model):
    alquiler = models.ForeignKey(
        AlquilerContenedor,
        on_delete=models.PROTECT,
        related_name="recibos",
        verbose_name="Alquiler de contenedor",
    )
    fecha_recibo = models.DateField(default=timezone.localdate, verbose_name="Fecha de recibo")
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Recibo de contenedor"
        verbose_name_plural = "Recibos de contenedores"
        ordering = ("-fecha_recibo", "-id")

    def clean(self):
        errors = {}
        if self.alquiler_id and self.alquiler.estado != AlquilerContenedor.Estado.ACTIVO:
            errors["alquiler"] = "Solo puedes recibir contenedores con alquiler activo."
        if self.alquiler_id and self.fecha_recibo and self.fecha_recibo < self.alquiler.fecha_inicio:
            errors["fecha_recibo"] = "La fecha de recibo no puede ser menor que la fecha de inicio del alquiler."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        alquiler = self.alquiler
        updates = []
        if alquiler.estado != AlquilerContenedor.Estado.CERRADO:
            alquiler.estado = AlquilerContenedor.Estado.CERRADO
            updates.append("estado")
        if not alquiler.fecha_fin or alquiler.fecha_fin != self.fecha_recibo:
            alquiler.fecha_fin = self.fecha_recibo
            updates.append("fecha_fin")
        if updates:
            alquiler.save(update_fields=updates)

    def __str__(self):
        return f"Recibo {self.pk} - {self.alquiler.contenedor.codigo}"
