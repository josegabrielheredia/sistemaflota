from django.contrib import admin

from .models import AbonoCuenta, Cuenta


class AbonoCuentaInline(admin.TabularInline):
    model = AbonoCuenta
    extra = 0


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "monto", "monto_pagado", "saldo_pendiente", "estado", "fecha_vencimiento")
    list_filter = ("tipo", "estado", "fecha_vencimiento")
    search_fields = ("nombre", "tercero", "categoria", "chofer__nombre")
    inlines = [AbonoCuentaInline]


@admin.register(AbonoCuenta)
class AbonoCuentaAdmin(admin.ModelAdmin):
    list_display = ("cuenta", "fecha", "monto", "metodo", "referencia")
    list_filter = ("metodo", "fecha")
    search_fields = ("cuenta__nombre", "referencia")
