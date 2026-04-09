from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils.html import format_html

from .forms import RegistroGastoForm
from .models import (
    Capacitacion,
    Cargo,
    Departamento,
    Empleado,
    Licencia,
    PagoEmpleado,
    RegistroGasto,
    TipoLicencia,
    Vacacion,
)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "departamento")
    search_fields = ("nombre", "departamento__nombre")


class LicenciaInline(admin.TabularInline):
    model = Licencia
    extra = 0


class VacacionInline(admin.TabularInline):
    model = Vacacion
    extra = 0
    fields = ("fecha_inicio", "fecha_fin", "pagada_sin_disfrute", "estado", "observaciones")
    readonly_fields = ("estado",)


class CapacitacionInline(admin.TabularInline):
    model = Capacitacion
    extra = 0
    fields = ("tema", "fecha_inicio", "fecha_fin", "costo", "proveedor", "observaciones")


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "cedula", "fecha_nacimiento", "departamento", "designacion", "estado")
    search_fields = ("nombre", "apellidos", "cedula", "telefono", "correo")
    inlines = [LicenciaInline, VacacionInline, CapacitacionInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "fecha_nacimiento" in form.base_fields:
            form.base_fields["fecha_nacimiento"].required = True
            form.base_fields["fecha_nacimiento"].help_text = (
                "Dato requerido para seguimiento de cumpleanos."
            )
        return form

    @admin.display(description="Empleado")
    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellidos}".strip()

    @admin.display(description="Departamento")
    def departamento(self, obj):
        return obj.cargo.departamento.nombre

    @admin.display(description="Designacion")
    def designacion(self, obj):
        return obj.cargo.nombre


@admin.register(TipoLicencia)
class TipoLicenciaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "requiere_aprobacion", "activo")
    search_fields = ("nombre",)


@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tipo", "fecha_inicio", "fecha_fin", "estado")
    search_fields = ("empleado__nombre", "tipo__nombre", "motivo")


@admin.register(Vacacion)
class VacacionAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha_inicio", "fecha_fin", "estado", "pagada_sin_disfrute")
    search_fields = ("empleado__nombre",)
    list_filter = ("estado", "pagada_sin_disfrute", "fecha_inicio", "fecha_fin")
    fields = (
        "empleado",
        "fecha_inicio",
        "fecha_fin",
        "pagada_sin_disfrute",
        "estado",
        "observaciones",
    )
    readonly_fields = ("estado",)

    def get_queryset(self, request):
        Vacacion.sincronizar_estados()
        return super().get_queryset(request)


@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tema", "fecha_inicio", "fecha_fin", "costo_rd", "proveedor")
    search_fields = ("empleado__nombre", "tema", "proveedor")

    @admin.display(description="Costo")
    def costo_rd(self, obj):
        if obj.costo is None:
            return "No aplica"
        return f"RD$ {obj.costo:,.2f}"


@admin.register(PagoEmpleado)
class PagoEmpleadoAdmin(admin.ModelAdmin):
    change_form_template = "admin/recursos_humanos/pagoempleado/change_form.html"
    list_display = (
        "empleado",
        "fecha",
        "quincena",
        "monto",
        "metodo",
        "referencia",
        "volante_link",
    )
    list_filter = ("fecha", "quincena", "metodo")
    search_fields = ("empleado__nombre", "empleado__apellidos", "empleado__cedula", "referencia")
    fields = ("empleado", "fecha", "quincena", "monto", "metodo", "referencia", "observaciones")

    def get_urls(self):
        custom_urls = [
            path(
                "<int:pago_id>/volante/",
                self.admin_site.admin_view(self.volante_view),
                name="recursos_humanos_pagoempleado_volante",
            ),
            path(
                "<int:pago_id>/despues-guardar/",
                self.admin_site.admin_view(self.after_save_view),
                name="recursos_humanos_pagoempleado_after_save",
            ),
        ]
        return custom_urls + super().get_urls()

    def volante_view(self, request, pago_id):
        pago = get_object_or_404(
            PagoEmpleado.objects.select_related("empleado", "empleado__cargo", "empleado__cargo__departamento"),
            pk=pago_id,
        )
        return render(
            request,
            "admin/recursos_humanos/pagoempleado/volante.html",
            {
                **self.admin_site.each_context(request),
                "title": f"Volante de pago #{pago.id}",
                "pago": pago,
            },
        )

    def after_save_view(self, request, pago_id):
        pago = get_object_or_404(PagoEmpleado, pk=pago_id)
        return render(
            request,
            "admin/recursos_humanos/pagoempleado/after_save.html",
            {
                **self.admin_site.each_context(request),
                "title": "Pago registrado",
                "pago": pago,
            },
        )

    @admin.display(description="Volante")
    def volante_link(self, obj):
        url = reverse("admin:recursos_humanos_pagoempleado_volante", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Imprimir</a>', url)

    def response_add(self, request, obj, post_url_continue=None):
        url = reverse("admin:recursos_humanos_pagoempleado_after_save", args=[obj.pk])
        return HttpResponseRedirect(url)


@admin.register(RegistroGasto)
class RegistroGastoAdmin(admin.ModelAdmin):
    form = RegistroGastoForm
    list_display = (
        "fecha",
        "proveedor",
        "motivo",
        "con_comprobante",
        "numero_comprobante",
        "valor",
        "itbis",
        "propinas",
        "total_rd",
    )
    list_filter = ("fecha", "con_comprobante", "proveedor")
    search_fields = ("proveedor", "motivo", "numero_comprobante")
    fieldsets = (
        (
            "Datos del gasto",
            {
                "fields": (
                    "fecha",
                    "con_comprobante",
                    "numero_comprobante",
                    "proveedor",
                    "motivo",
                )
            },
        ),
        (
            "Monto",
            {
                "fields": (
                    "valor",
                    "itbis",
                    "propinas",
                    "observaciones",
                )
            },
        ),
    )

    class Media:
        js = ("admin/js/rrhh_gastos_admin.js",)

    @admin.display(description="Total")
    def total_rd(self, obj):
        return f"RD$ {obj.total:,.2f}"
