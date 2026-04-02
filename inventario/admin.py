from django.contrib import admin

from .models import MovimientoInventario, Producto


class MovimientoInventarioInline(admin.TabularInline):
    model = MovimientoInventario
    extra = 0


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "unidad_medida", "cantidad", "precio", "activo")
    search_fields = ("nombre", "descripcion")
    inlines = [MovimientoInventarioInline]


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ("producto", "tipo", "cantidad", "fecha", "referencia")
    search_fields = ("producto__nombre", "referencia")
