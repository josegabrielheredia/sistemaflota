from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils.html import format_html

from .models import AlquilerContenedor, Chasis, Contenedor, ReciboContenedor, Vehiculo


class ReciboContenedorAdminForm(forms.ModelForm):
    class Meta:
        model = ReciboContenedor
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = AlquilerContenedor.objects.select_related("contenedor", "chasis").filter(
            estado=AlquilerContenedor.Estado.ACTIVO
        )
        if self.instance.pk and self.instance.alquiler_id:
            queryset = AlquilerContenedor.objects.select_related("contenedor", "chasis").filter(
                pk=self.instance.alquiler_id
            ) | queryset
        self.fields["alquiler"].queryset = queryset.order_by("-fecha_inicio", "contenedor__codigo").distinct()


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
        "numero_factura",
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
                "title": f"Factura de alquiler #{self.numero_factura(alquiler)}",
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

    @admin.display(description="Numero de factura")
    def numero_factura(self, obj):
        return f"ALQ-{obj.pk:05d}"

    def response_add(self, request, obj, post_url_continue=None):
        url = reverse("admin:tracking_alquilercontenedor_after_save", args=[obj.pk])
        return HttpResponseRedirect(url)


@admin.register(ReciboContenedor)
class ReciboContenedorAdmin(admin.ModelAdmin):
    change_form_template = "admin/tracking/recibocontenedor/change_form.html"
    form = ReciboContenedorAdminForm
    list_display = (
        "numero_recibo",
        "contenedor",
        "cliente",
        "fecha_recibo",
        "volante_link",
    )
    search_fields = ("alquiler__contenedor__codigo", "alquiler__cliente")
    list_filter = ("fecha_recibo",)
    fieldsets = (
        (
            "Recibo de contenedor",
            {"fields": ("alquiler", "fecha_recibo", "observaciones")},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("alquiler", "alquiler__contenedor", "alquiler__chasis")

    def get_urls(self):
        custom_urls = [
            path(
                "<int:recibo_id>/volante/",
                self.admin_site.admin_view(self.volante_view),
                name="tracking_recibocontenedor_volante",
            ),
            path(
                "<int:recibo_id>/despues-guardar/",
                self.admin_site.admin_view(self.after_save_view),
                name="tracking_recibocontenedor_after_save",
            ),
        ]
        return custom_urls + super().get_urls()

    def volante_view(self, request, recibo_id):
        recibo = get_object_or_404(
            ReciboContenedor.objects.select_related("alquiler", "alquiler__contenedor", "alquiler__chasis"),
            pk=recibo_id,
        )
        return render(
            request,
            "admin/tracking/recibocontenedor/volante.html",
            {
                **self.admin_site.each_context(request),
                "title": f"Volante de recibo #{self.numero_recibo(recibo)}",
                "recibo": recibo,
            },
        )

    def after_save_view(self, request, recibo_id):
        recibo = get_object_or_404(ReciboContenedor, pk=recibo_id)
        return render(
            request,
            "admin/tracking/recibocontenedor/after_save.html",
            {
                **self.admin_site.each_context(request),
                "title": "Recibo registrado",
                "recibo": recibo,
            },
        )

    @admin.display(description="Numero de recibo")
    def numero_recibo(self, obj):
        return f"REC-{obj.pk:05d}"

    @admin.display(description="Contenedor")
    def contenedor(self, obj):
        return obj.alquiler.contenedor.codigo

    @admin.display(description="Cliente")
    def cliente(self, obj):
        return obj.alquiler.cliente

    @admin.display(description="Volante")
    def volante_link(self, obj):
        url = reverse("admin:tracking_recibocontenedor_volante", args=[obj.pk])
        return format_html('<a href="{}" target="_blank">Imprimir</a>', url)

    def response_add(self, request, obj, post_url_continue=None):
        url = reverse("admin:tracking_recibocontenedor_after_save", args=[obj.pk])
        return HttpResponseRedirect(url)
