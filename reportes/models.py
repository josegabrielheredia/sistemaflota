from django.db import models


class Reporte(models.Model):
    class Categoria(models.TextChoices):
        OPERATIVO = "operativo", "Operativo"
        FINANCIERO = "financiero", "Financiero"
        RRHH = "rrhh", "RRHH"
        FLOTA = "flota", "Flota"
        OTRO = "otro", "Otro"

    titulo = models.CharField(max_length=100)
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.OPERATIVO,
    )
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.TextField()

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ("-fecha", "-id")

    def __str__(self):
        return self.titulo
