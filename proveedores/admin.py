from django.contrib import admin
from django.db.models import Sum

from .models import Proveedor, RegistroProveedor


class RegistroProveedorInline(admin.TabularInline):
    model = RegistroProveedor
    extra = 1
    verbose_name = "Registro operativo"
    verbose_name_plural = "Registros operativos (trabajar debajo de la empresa)"
    fields = (
        "fecha",
        "placa",
        "ruta",
        "numero_transporte",
        "destino",
        "tarifa",
    )


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo", "fecha_registro", "total_registros", "total_tarifas")
    search_fields = ("nombre",)
    list_filter = ("activo", "fecha_registro")
    fieldsets = (
        ("Empresa proveedora", {"fields": ("nombre", "activo")}),
        ("Control", {"fields": ("fecha_registro",)}),
    )
    readonly_fields = ("fecha_registro",)
    inlines = [RegistroProveedorInline]

    @admin.display(description="Registros")
    def total_registros(self, obj):
        return obj.registros.count()

    @admin.display(description="Tarifa acumulada")
    def total_tarifas(self, obj):
        total = obj.registros.aggregate(total=Sum("tarifa"))["total"] or 0
        return f"RD$ {total:,.2f}"


@admin.register(RegistroProveedor)
class RegistroProveedorAdmin(admin.ModelAdmin):
    list_display = (
        "fecha",
        "proveedor",
        "placa",
        "ruta",
        "numero_transporte",
        "destino",
        "tarifa_rd",
    )
    list_filter = ("fecha", "proveedor")
    search_fields = (
        "proveedor__nombre",
        "placa",
        "ruta",
        "numero_transporte",
        "destino",
    )
    fieldsets = (
        (
            "Empresa proveedora",
            {
                "fields": ("proveedor",),
                "description": "Selecciona una empresa creada. Si no aparece en la lista, usa el boton + para crearla en el momento.",
            },
        ),
        (
            "Registro operativo",
            {
                "fields": (
                    "fecha",
                    "placa",
                    "ruta",
                    "numero_transporte",
                    "destino",
                    "tarifa",
                    "observaciones",
                )
            },
        ),
    )
    list_select_related = ("proveedor",)

    @admin.display(description="Tarifa")
    def tarifa_rd(self, obj):
        return f"RD$ {obj.tarifa:,.2f}"
