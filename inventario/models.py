from django.db import models


class Producto(models.Model):
    class Categoria(models.TextChoices):
        COMBUSTIBLE = "combustible", "Combustible"
        INSUMO = "insumo", "Insumo"
        REPUESTO = "repuesto", "Repuesto"
        OTRO = "otro", "Otro"

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.INSUMO,
    )
    unidad_medida = models.CharField(max_length=20, default="unidad")
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ("nombre",)

    def __str__(self):
        return self.nombre


class MovimientoInventario(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SALIDA = "salida", "Salida"
        AJUSTE = "ajuste", "Ajuste"

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="movimientos",
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    referencia = models.CharField(max_length=120, blank=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Movimiento de inventario"
        verbose_name_plural = "Movimientos de inventario"
        ordering = ("-fecha", "-id")

    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo}"


class SuministroCombustible(models.Model):
    class EstadoPago(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PARCIAL = "parcial", "Parcial"
        PAGADO = "pagado", "Pagado"

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="suministros",
    )
    chofer = models.ForeignKey(
        "choferes.Chofer",
        on_delete=models.CASCADE,
        related_name="suministros_combustible",
    )
    vehiculo = models.ForeignKey(
        "tracking.Vehiculo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suministros_combustible",
    )
    fecha = models.DateField(auto_now_add=True)
    cantidad = models.DecimalField(max_digits=12, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    monto_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado_pago = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE,
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Suministro de combustible"
        verbose_name_plural = "Suministros de combustible"
        ordering = ("-fecha", "-id")

    def __str__(self):
        return f"{self.chofer.nombre} - {self.producto.nombre}"
