from django.contrib import admin

from .models import Pago


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("chofer", "conduce", "monto", "metodo", "fecha")
    list_filter = ("metodo", "fecha")
    search_fields = ("chofer__nombre", "conduce__numero", "referencia")
