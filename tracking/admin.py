from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils.html import format_html

from .models import AlquilerContenedor, Chasis, Contenedor, Vehiculo


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
        "tamano_pies",
        "color",
        "local_o_importado",
        "estado",
    )
    search_fields = ("codigo", "color", "ubicacion_actual")
    list_filter = ("estado", "local_o_importado")
    fieldsets = (
        (
            "Datos del contenedor",
            {"fields": ("codigo", "tamano_pies", "color", "local_o_importado", "estado")},
        ),
        (
            "Ubicacion",
            {
                "fields": (
                    "ubicacion_actual",
                    "observaciones",
                )
            },
        ),
    )


@admin.register(Chasis)
class ChasisAdmin(admin.ModelAdmin):
    list_display = ("codigo", "tamano_pies", "estado", "ubicacion_actual")
    search_fields = ("codigo", "ubicacion_actual")
    list_filter = ("estado",)
    fieldsets = (
        ("Datos del chasis", {"fields": ("codigo", "tamano_pies", "estado")}),
        ("Ubicacion", {"fields": ("ubicacion_actual", "observaciones")}),
    )


@admin.register(AlquilerContenedor)
class AlquilerContenedorAdmin(admin.ModelAdmin):
    change_form_template = "admin/tracking/alquilercontenedor/change_form.html"
    list_display = (
        "contenedor",
        "estado",
        "cliente",
        "con_chasis",
        "chasis",
        "fecha_inicio",
        "fecha_fin",
        "costo_alquiler",
        "forma_pago",
        "factura_link",
    )
    list_filter = ("estado", "con_chasis", "forma_pago", "fecha_inicio")
    search_fields = ("contenedor__codigo", "chasis__codigo", "cliente", "referido_por")
    fieldsets = (
        (
            "Contenedor",
            {"fields": ("contenedor", "con_chasis", "chasis")},
        ),
        (
            "Cliente y referencias",
            {
                "fields": (
                    "cliente",
                    "referido_por",
                    "numero_contacto_referencia",
                    "numero_contrato_compromiso",
                )
            },
        ),
        (
            "Periodo de alquiler",
            {"fields": ("fecha_inicio", "fecha_fin", "estado")},
        ),
        (
            "Pago",
            {"fields": ("costo_alquiler", "forma_pago", "numero_referencia_pago")},
        ),
        (
            "Observaciones",
            {"fields": ("observaciones",)},
        ),
    )

    class Media:
        js = ("admin/js/alquiler_contenedor_admin.js",)

    def get_urls(self):
        custom_urls = [
            path(
                "<int:alquiler_id>/factura/",
                self.admin_site.admin_view(self.factura_view),
                name="tracking_alquilercontenedor_factura",
            ),
            path(
                "<int:alquiler_id>/despues-guardar/",
                self.admin_site.admin_view(self.after_save_view),
                name="tracking_alquilercontenedor_after_save",
            ),
        ]
        return custom_urls + super().get_urls()

    def factura_view(self, request, alquiler_id):
        alquiler = get_object_or_404(
            AlquilerContenedor.objects.select_related("contenedor", "chasis"),
            pk=alquiler_id,
        )
        return render(
            request,
            "admin/tracking/alquilercontenedor/factura.html",
            {
                **self.admin_site.each_context(request),
                "title": f"Factura de alquiler #{alquiler.id}",
                "alquiler": alquiler,
            },
        )

    def after_save_view(self, request, alquiler_id):
        alquiler = get_object_or_404(AlquilerContenedor, pk=alquiler_id)
        return render(
            request,
            "admin/tracking/alquilercontenedor/after_save.html",
            {
                **self.admin_site.each_context(request),
                "title": "Alquiler registrado",
                "alquiler": alquiler,
            },
        )

    @admin.display(description="Factura")
    def factura_link(self, obj):
        url = reverse("admin:tracking_alquilercontenedor_factura", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Imprimir</a>', url)

    def response_add(self, request, obj, post_url_continue=None):
        url = reverse("admin:tracking_alquilercontenedor_after_save", args=[obj.pk])
        return HttpResponseRedirect(url)
