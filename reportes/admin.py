from django.contrib import admin
from django.template.response import TemplateResponse

from .forms import GeneradorReporteForm
from .models import Reporte
from .views import _build_report, _export_report_to_excel


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    change_list_template = "admin/reportes/reporte/change_list.html"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        form = GeneradorReporteForm(request.GET or None)
        selected_report = None

        if form.is_valid():
            selected_report = _build_report(
                form.cleaned_data["tipo_reporte"],
                form.cleaned_data.get("fecha_desde"),
                form.cleaned_data.get("fecha_hasta"),
            )
            if request.GET.get("action") == "excel" and selected_report:
                return _export_report_to_excel(selected_report)

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Generador de reportes",
            "subtitle": "Reportes",
            "form": form,
            "selected_report": selected_report,
            "has_add_permission": False,
            "is_popup": False,
            "save_as": False,
            "cl": None,
        }
        if extra_context:
            context.update(extra_context)
        return TemplateResponse(request, self.change_list_template, context)
