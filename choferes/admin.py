from django.contrib import admin

from .models import Chofer, Conduce


class ConduceInline(admin.TabularInline):
    model = Conduce
    extra = 0


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "cedula",
        "licencia",
        "categoria_licencia",
        "metodo_pago_preferido",
        "honorario_referencial",
        "estado",
    )
    search_fields = ("nombre", "cedula", "licencia", "telefono", "banco", "titular_cuenta", "numero_cuenta")
    fieldsets = (
        ("Identificacion", {"fields": ("nombre", "cedula", "telefono", "direccion")}),
        ("Documentacion", {"fields": ("licencia", "categoria_licencia", "vencimiento_licencia", "estado")}),
        ("Pago por servicio", {"fields": ("metodo_pago_preferido", "banco", "titular_cuenta", "numero_cuenta", "honorario_referencial")}),
        ("Seguimiento", {"fields": ("fecha_registro", "observaciones")}),
    )
    readonly_fields = ("fecha_registro",)
    inlines = [ConduceInline]


@admin.register(Conduce)
class ConduceAdmin(admin.ModelAdmin):
    list_display = ("numero", "chofer", "vehiculo", "fecha", "monto_generado", "estado")
    search_fields = ("numero", "chofer__nombre", "vehiculo__placa", "origen", "destino")
