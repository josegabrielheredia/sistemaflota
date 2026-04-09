from django.contrib import admin

from .models import Contenedor, Vehiculo


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = (
        "placa",
        "marca",
        "modelo",
        "estado",
        "propiedad",
        "dueno_nombre",
        "cliente_actual",
        "fecha_retorno_estimada",
    )
    search_fields = (
        "placa",
        "codigo_interno",
        "marca",
        "modelo",
        "cliente_actual",
        "dueno_nombre",
        "dueno_documento",
    )
    list_filter = ("estado", "es_propiedad_empresa")
    fieldsets = (
        (
            "Identificacion del vehiculo",
            {"fields": ("placa", "codigo_interno", "marca", "modelo", "anio", "tipo", "capacidad", "color")},
        ),
        (
            "Propiedad",
            {"fields": ("es_propiedad_empresa", "dueno_nombre", "dueno_documento", "dueno_telefono")},
        ),
        (
            "Operacion",
            {
                "fields": (
                    "estado",
                    "ultima_ubicacion",
                    "cliente_actual",
                    "fecha_salida",
                    "fecha_retorno_estimada",
                    "observaciones",
                )
            },
        ),
    )

    @admin.display(description="Propiedad")
    def propiedad(self, obj):
        return "Empresa" if obj.es_propiedad_empresa else "Alquilado"


@admin.register(Contenedor)
class ContenedorAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "color",
        "local_o_importado",
        "estado",
        "cliente_actual",
        "fecha_salida",
        "fecha_retorno_estimada",
        "costo_alquiler",
        "forma_pago",
    )
    search_fields = ("codigo", "color", "cliente_actual", "referido_por", "servicio_a")
    list_filter = ("estado", "local_o_importado", "forma_pago")
    fieldsets = (
        (
            "Datos del contenedor",
            {"fields": ("codigo", "color", "local_o_importado", "estado")},
        ),
        (
            "Alquiler",
            {
                "fields": (
                    "cliente_actual",
                    "fecha_salida",
                    "fecha_retorno_estimada",
                    "costo_alquiler",
                    "forma_pago",
                    "numero_referencia_pago",
                    "referido_por",
                    "servicio_a",
                    "observaciones",
                )
            },
        ),
    )

    class Media:
        js = ("admin/js/contenedor_admin.js",)
