from urllib.parse import urlencode

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from choferes.models import Chofer
from cuentas.models import Cuenta
from inventario.models import SuministroCombustible
from pagos.models import Pago
from recursos_humanos.models import Empleado, Licencia, Vacacion
from tracking.models import Vehiculo

from .forms import GeneradorReporteForm


def _format_currency(value):
    return f"RD$ {value:,.2f}"


def _slugify_filename(value):
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    return "_".join(part for part in normalized.split("_") if part)


def _export_report_to_excel(report):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Reporte"

    sheet["A1"] = report["title"]
    sheet["A1"].font = Font(bold=True, size=14)
    sheet["A2"] = report["description"]
    sheet["A2"].font = Font(italic=True, size=10)

    header_row = 4
    fill = PatternFill("solid", fgColor="DCEBFF")
    for column_index, column_name in enumerate(report["columns"], start=1):
        cell = sheet.cell(row=header_row, column=column_index, value=column_name)
        cell.font = Font(bold=True)
        cell.fill = fill

    for row_index, row in enumerate(report["rows"], start=header_row + 1):
        for column_index, value in enumerate(row, start=1):
            sheet.cell(row=row_index, column=column_index, value=value)

    footer_row = header_row + len(report["rows"]) + 2
    sheet.cell(row=footer_row, column=1, value=report["total_label"]).font = Font(bold=True)
    sheet.cell(row=footer_row, column=2, value=str(report["total_value"])).font = Font(bold=True)

    for column_cells in sheet.columns:
        length = max(len(str(cell.value or "")) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = min(length + 4, 42)

    filename = f"{_slugify_filename(report['title'])}.xlsx"
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response


def _build_report(tipo_reporte):
    hoy = timezone.localdate()

    if tipo_reporte == "choferes_registrados":
        registros = list(
            Chofer.objects.all()
            .order_by("nombre")
            .values("nombre", "cedula", "licencia", "metodo_pago_preferido", "estado")
        )
        return {
            "title": "Choferes subcontratistas registrados",
            "description": "Listado general de choferes subcontratistas disponibles en el sistema.",
            "columns": ["Nombre", "Cedula", "Licencia", "Pago preferido", "Estado"],
            "rows": [
                [
                    item["nombre"],
                    item["cedula"],
                    item["licencia"],
                    item["metodo_pago_preferido"] or "No definido",
                    item["estado"],
                ]
                for item in registros
            ],
            "total_label": "Choferes encontrados",
            "total_value": len(registros),
        }

    if tipo_reporte == "empleados_activos":
        registros = list(
            Empleado.objects.filter(estado=Empleado.Estado.ACTIVO)
            .select_related("cargo", "cargo__departamento")
            .order_by("nombre")
        )
        return {
            "title": "Empleados activos",
            "description": "Personal interno activo actualmente en la empresa.",
            "columns": ["Nombre", "Cedula", "Cargo", "Departamento", "Ingreso"],
            "rows": [
                [
                    item.nombre,
                    item.cedula,
                    item.cargo.nombre,
                    item.cargo.departamento.nombre,
                    item.fecha_ingreso.strftime("%d/%m/%Y"),
                ]
                for item in registros
            ],
            "total_label": "Empleados activos",
            "total_value": len(registros),
        }

    if tipo_reporte == "licencias_activas":
        registros = list(
            Licencia.objects.select_related("empleado", "tipo")
            .filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy)
            .order_by("fecha_inicio")
        )
        return {
            "title": "Licencias activas",
            "description": "Colaboradores que se encuentran actualmente bajo licencia.",
            "columns": ["Empleado", "Tipo", "Inicio", "Fin", "Estado"],
            "rows": [
                [
                    item.empleado.nombre,
                    item.tipo.nombre,
                    item.fecha_inicio.strftime("%d/%m/%Y"),
                    item.fecha_fin.strftime("%d/%m/%Y"),
                    item.get_estado_display(),
                ]
                for item in registros
            ],
            "total_label": "Licencias activas",
            "total_value": len(registros),
        }

    if tipo_reporte == "vacaciones_activas":
        registros = list(
            Vacacion.objects.select_related("empleado")
            .filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy)
            .order_by("fecha_inicio")
        )
        return {
            "title": "Vacaciones activas",
            "description": "Empleados que actualmente se encuentran de vacaciones.",
            "columns": ["Empleado", "Inicio", "Fin", "Estado"],
            "rows": [
                [
                    item.empleado.nombre,
                    item.fecha_inicio.strftime("%d/%m/%Y"),
                    item.fecha_fin.strftime("%d/%m/%Y"),
                    item.get_estado_display(),
                ]
                for item in registros
            ],
            "total_label": "Vacaciones activas",
            "total_value": len(registros),
        }

    if tipo_reporte == "pagos_por_mes":
        registros = list(
            Pago.objects.annotate(periodo=TruncMonth("fecha"))
            .values("periodo")
            .annotate(total=Sum("monto"), cantidad=Count("id"))
            .order_by("-periodo")
        )
        return {
            "title": "Total pagado a choferes por mes",
            "description": "Consolidado mensual de pagos realizados a choferes subcontratistas.",
            "columns": ["Mes", "Total pagado"],
            "rows": [
                [
                    item["periodo"].strftime("%m/%Y") if item["periodo"] else "Sin fecha",
                    _format_currency(item["total"] or 0),
                ]
                for item in registros
            ],
            "total_label": "Total general pagado",
            "total_value": _format_currency(Pago.objects.aggregate(total=Sum("monto"))["total"] or 0),
        }

    if tipo_reporte == "vehiculos_disponibles":
        registros = list(
            Vehiculo.objects.filter(estado=Vehiculo.Estado.DISPONIBLE)
            .order_by("placa")
            .values("placa", "marca", "modelo", "ultima_ubicacion")
        )
        return {
            "title": "Vehiculos disponibles",
            "description": "Unidades actualmente disponibles para asignacion o servicio.",
            "columns": ["Placa", "Marca", "Modelo", "Ultima ubicacion"],
            "rows": [
                [
                    item["placa"],
                    item["marca"] or "N/D",
                    item["modelo"],
                    item["ultima_ubicacion"] or "N/D",
                ]
                for item in registros
            ],
            "total_label": "Vehiculos disponibles",
            "total_value": len(registros),
        }

    if tipo_reporte == "cuentas_pendientes":
        registros = list(
            Cuenta.objects.filter(estado__in=[Cuenta.Estado.PENDIENTE, Cuenta.Estado.PARCIAL, Cuenta.Estado.VENCIDA])
            .order_by("fecha_vencimiento", "nombre")
        )
        return {
            "title": "Cuentas pendientes",
            "description": "Obligaciones y saldos que aun requieren seguimiento financiero.",
            "columns": ["Concepto", "Tipo", "Vencimiento", "Saldo pendiente", "Estado"],
            "rows": [
                [
                    item.nombre,
                    item.get_tipo_display(),
                    item.fecha_vencimiento.strftime("%d/%m/%Y"),
                    _format_currency(item.saldo_pendiente),
                    item.get_estado_display(),
                ]
                for item in registros
            ],
            "total_label": "Saldo pendiente total",
            "total_value": _format_currency(
                Cuenta.objects.filter(
                    estado__in=[Cuenta.Estado.PENDIENTE, Cuenta.Estado.PARCIAL, Cuenta.Estado.VENCIDA]
                ).aggregate(total=Sum("saldo_pendiente"))["total"] or 0
            ),
        }

    if tipo_reporte == "combustible_pendiente":
        registros = list(
            SuministroCombustible.objects.select_related("chofer", "producto", "vehiculo")
            .filter(saldo_pendiente__gt=0)
            .order_by("-fecha", "-id")
        )
        return {
            "title": "Suministros de combustible pendientes",
            "description": "Despachos de combustible con saldo pendiente de cobro o pago parcial.",
            "columns": ["Fecha", "Chofer", "Producto", "Vehiculo", "Saldo pendiente"],
            "rows": [
                [
                    item.fecha.strftime("%d/%m/%Y"),
                    item.chofer.nombre,
                    item.producto.nombre,
                    item.vehiculo.placa if item.vehiculo else "N/D",
                    _format_currency(item.saldo_pendiente),
                ]
                for item in registros
            ],
            "total_label": "Saldo pendiente total",
            "total_value": _format_currency(
                SuministroCombustible.objects.filter(saldo_pendiente__gt=0).aggregate(total=Sum("saldo_pendiente"))["total"] or 0
            ),
        }

    return None


def lista_reportes(request):
    form = GeneradorReporteForm(request.GET or None)
    selected_report = None

    if form.is_valid():
        selected_report = _build_report(form.cleaned_data["tipo_reporte"])
        if request.GET.get("export") == "excel" and selected_report:
            return _export_report_to_excel(selected_report)

    return render(
        request,
        "reportes/lista_reportes.html",
        {
            "page_title": "Reportes",
            "page_intro": "Genera reportes operativos, financieros y de personal desde un solo panel.",
            "summary_cards": [
                {"label": "Choferes", "value": Chofer.objects.count(), "accent": "blue"},
                {"label": "Pagos", "value": Pago.objects.count(), "accent": "green"},
                {"label": "Cuentas pendientes", "value": Cuenta.objects.filter(estado__in=[Cuenta.Estado.PENDIENTE, Cuenta.Estado.PARCIAL, Cuenta.Estado.VENCIDA]).count(), "accent": "amber"},
            ],
            "form": form,
            "selected_report": selected_report,
            "excel_query": urlencode(
                {
                    "tipo_reporte": form.cleaned_data["tipo_reporte"],
                    "export": "excel",
                }
            )
            if form.is_valid() and selected_report
            else "",
        },
    )
