from django.contrib import admin

from .models import MovimientoInventario, Producto, SuministroCombustible


class MovimientoInventarioInline(admin.TabularInline):
    model = MovimientoInventario
    extra = 0


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "unidad_medida", "cantidad", "precio", "activo")
    list_filter = ("categoria", "activo")
    search_fields = ("nombre", "descripcion")
    inlines = [MovimientoInventarioInline]


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ("producto", "tipo", "cantidad", "fecha", "referencia")
    list_filter = ("tipo", "fecha")
    search_fields = ("producto__nombre", "referencia")


@admin.register(SuministroCombustible)
class SuministroCombustibleAdmin(admin.ModelAdmin):
    list_display = ("producto", "chofer", "vehiculo", "cantidad", "precio_unitario", "estado_pago", "fecha")
    list_filter = ("estado_pago", "fecha", "producto")
    search_fields = ("chofer__nombre", "vehiculo__placa", "producto__nombre")
