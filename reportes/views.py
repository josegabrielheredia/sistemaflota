from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from choferes.models import Chofer, Conduce
from inventario.models import MovimientoInventario, Producto, SuministroCombustible
from pagos.models import Pago
from recursos_humanos.models import Empleado, Licencia, PagoEmpleado, TipoLicencia, Vacacion
from tracking.models import Vehiculo

from .forms import GeneradorReporteForm


def _format_currency(value):
    return f"RD$ {value:,.2f}"


def _choice_label(choices, value, default="No definido"):
    mapping = dict(choices)
    return mapping.get(value, value or default)


def _slugify_filename(value):
    normalized = "".join(char.lower() if char.isalnum() else "_" for char in value)
    return "_".join(part for part in normalized.split("_") if part)


def _apply_date_range(queryset, field_name, fecha_desde=None, fecha_hasta=None):
    filters = {}
    if fecha_desde:
        filters[f"{field_name}__gte"] = fecha_desde
    if fecha_hasta:
        filters[f"{field_name}__lte"] = fecha_hasta
    return queryset.filter(**filters) if filters else queryset


def _filter_period_overlap(queryset, start_field, end_field, fecha_desde=None, fecha_hasta=None):
    if fecha_desde:
        queryset = queryset.filter(**{f"{end_field}__gte": fecha_desde})
    if fecha_hasta:
        queryset = queryset.filter(**{f"{start_field}__lte": fecha_hasta})
    return queryset


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


def _build_report(tipo_reporte, fecha_desde=None, fecha_hasta=None):
    hoy = timezone.localdate()

    if tipo_reporte == "choferes_registrados":
        registros = list(
            _apply_date_range(Chofer.objects.all(), "fecha_registro", fecha_desde, fecha_hasta)
            .order_by("nombre")
            .values("nombre", "cedula", "licencia", "carta_buena_conducta", "rntt")
        )
        return {
            "title": "Choferes subcontratistas registrados",
            "description": "Listado general de choferes subcontratistas disponibles en el sistema.",
            "columns": ["Nombre", "Cedula", "Licencia", "Carta buena conducta", "RNTT"],
            "rows": [
                [
                    item["nombre"],
                    item["cedula"],
                    item["licencia"],
                    "Si" if item["carta_buena_conducta"] else "No",
                    "Si" if item["rntt"] else "No",
                ]
                for item in registros
            ],
            "total_label": "Choferes encontrados",
            "total_value": len(registros),
        }

    if tipo_reporte == "empleados_activos":
        registros = list(
            _apply_date_range(
                Empleado.objects.filter(estado=Empleado.Estado.ACTIVO),
                "fecha_ingreso",
                fecha_desde,
                fecha_hasta,
            )
            .select_related("cargo", "cargo__departamento")
            .order_by("nombre")
        )
        return {
            "title": "Empleados activos",
            "description": "Personal interno activo actualmente en la empresa.",
            "columns": ["Nombre", "Cedula", "Cargo", "Departamento", "Ingreso"],
            "rows": [
                [
                    f"{item.nombre} {item.apellidos}".strip(),
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

    if tipo_reporte == "choferes_por_estado":
        registros = list(
            _apply_date_range(Chofer.objects.all(), "fecha_registro", fecha_desde, fecha_hasta)
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )
        return {
            "title": "Choferes por estado",
            "description": "Resumen de choferes subcontratistas agrupados por estado operativo.",
            "columns": ["Estado", "Cantidad"],
            "rows": [[_choice_label(Chofer.Estado.choices, item["estado"]), item["total"]] for item in registros],
            "total_label": "Choferes registrados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "choferes_carta_buena_conducta":
        registros = list(
            _apply_date_range(Chofer.objects.all(), "fecha_registro", fecha_desde, fecha_hasta)
            .values("carta_buena_conducta")
            .annotate(total=Count("id"))
            .order_by("carta_buena_conducta")
        )
        return {
            "title": "Choferes por carta de buena conducta",
            "description": "Resumen de choferes segun disponibilidad de carta de buena conducta.",
            "columns": ["Carta de buena conducta", "Cantidad"],
            "rows": [["Si" if item["carta_buena_conducta"] else "No", item["total"]] for item in registros],
            "total_label": "Choferes contabilizados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "choferes_rntt":
        registros = list(
            _apply_date_range(Chofer.objects.all(), "fecha_registro", fecha_desde, fecha_hasta)
            .values("rntt")
            .annotate(total=Count("id"))
            .order_by("rntt")
        )
        return {
            "title": "Choferes por cumplimiento de RNTT",
            "description": "Resumen de choferes segun cumplimiento del requisito interno RNTT.",
            "columns": ["RNTT", "Cantidad"],
            "rows": [["Si" if item["rntt"] else "No", item["total"]] for item in registros],
            "total_label": "Choferes contabilizados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "conduces_por_estado":
        registros = list(
            _apply_date_range(Conduce.objects.all(), "fecha", fecha_desde, fecha_hasta)
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )
        return {
            "title": "Conduces por estado",
            "description": "Resumen del flujo de conduces segun su estado actual.",
            "columns": ["Estado", "Cantidad"],
            "rows": [[_choice_label(Conduce.Estado.choices, item["estado"]), item["total"]] for item in registros],
            "total_label": "Conduces registrados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "licencias_activas":
        registros = list(
            _filter_period_overlap(
                Licencia.objects.select_related("empleado", "tipo")
                .filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy),
                "fecha_inicio",
                "fecha_fin",
                fecha_desde,
                fecha_hasta,
            )
            .order_by("fecha_inicio")
        )
        return {
            "title": "Licencias activas",
            "description": "Colaboradores que se encuentran actualmente bajo licencia.",
            "columns": ["Empleado", "Tipo", "Inicio", "Fin", "Estado"],
            "rows": [
                [
                    f"{item.empleado.nombre} {item.empleado.apellidos}".strip(),
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

    if tipo_reporte == "empleados_por_estado":
        registros = list(
            _apply_date_range(Empleado.objects.all(), "fecha_ingreso", fecha_desde, fecha_hasta)
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )
        return {
            "title": "Empleados por estado",
            "description": "Clasificacion del personal interno por estado laboral.",
            "columns": ["Estado", "Cantidad"],
            "rows": [[_choice_label(Empleado.Estado.choices, item["estado"]), item["total"]] for item in registros],
            "total_label": "Empleados contabilizados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "empleados_por_departamento":
        registros = list(
            _apply_date_range(Empleado.objects.all(), "fecha_ingreso", fecha_desde, fecha_hasta)
            .values("cargo__departamento__nombre")
            .annotate(total=Count("id"))
            .order_by("cargo__departamento__nombre")
        )
        return {
            "title": "Empleados por departamento",
            "description": "Distribucion del personal interno por departamento.",
            "columns": ["Departamento", "Cantidad"],
            "rows": [[item["cargo__departamento__nombre"] or "Sin departamento", item["total"]] for item in registros],
            "total_label": "Empleados contabilizados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "licencias_por_estado":
        registros = list(
            _filter_period_overlap(Licencia.objects.all(), "fecha_inicio", "fecha_fin", fecha_desde, fecha_hasta)
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )
        return {
            "title": "Licencias por estado",
            "description": "Resumen de licencias registradas segun su estado.",
            "columns": ["Estado", "Cantidad"],
            "rows": [[_choice_label(Licencia.Estado.choices, item["estado"]), item["total"]] for item in registros],
            "total_label": "Licencias contabilizadas",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "tipos_licencia_configurados":
        registros = list(
            TipoLicencia.objects.values("nombre", "requiere_aprobacion", "activo")
            .annotate(total=Count("id"))
            .order_by("nombre")
        )
        return {
            "title": "Tipos de licencia configurados",
            "description": "Catalogo de tipos de licencia configurados en RRHH.",
            "columns": ["Tipo de licencia", "Requiere aprobacion", "Activo"],
            "rows": [
                [item["nombre"], "Si" if item["requiere_aprobacion"] else "No", "Si" if item["activo"] else "No"]
                for item in registros
            ],
            "total_label": "Tipos configurados",
            "total_value": len(registros),
        }

    if tipo_reporte == "vacaciones_activas":
        registros = list(
            _filter_period_overlap(
                Vacacion.objects.select_related("empleado")
                .filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy),
                "fecha_inicio",
                "fecha_fin",
                fecha_desde,
                fecha_hasta,
            )
            .order_by("fecha_inicio")
        )
        return {
            "title": "Vacaciones activas",
            "description": "Empleados que actualmente se encuentran de vacaciones.",
            "columns": ["Empleado", "Inicio", "Fin", "Estado"],
            "rows": [
                [
                    f"{item.empleado.nombre} {item.empleado.apellidos}".strip(),
                    item.fecha_inicio.strftime("%d/%m/%Y"),
                    item.fecha_fin.strftime("%d/%m/%Y"),
                    item.get_estado_display(),
                ]
                for item in registros
            ],
            "total_label": "Vacaciones activas",
            "total_value": len(registros),
        }

    if tipo_reporte == "vacaciones_por_estado":
        registros = list(
            _filter_period_overlap(Vacacion.objects.all(), "fecha_inicio", "fecha_fin", fecha_desde, fecha_hasta)
            .values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )
        return {
            "title": "Vacaciones por estado",
            "description": "Resumen de vacaciones segun su estado de ejecucion.",
            "columns": ["Estado", "Cantidad"],
            "rows": [[_choice_label(Vacacion.Estado.choices, item["estado"]), item["total"]] for item in registros],
            "total_label": "Vacaciones contabilizadas",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "pagos_empleados_por_mes":
        registros = list(
            _apply_date_range(PagoEmpleado.objects.all(), "fecha", fecha_desde, fecha_hasta)
            .annotate(periodo=TruncMonth("fecha"))
            .values("periodo")
            .annotate(total=Sum("monto"), cantidad=Count("id"))
            .order_by("-periodo")
        )
        return {
            "title": "Pagos de empleados por mes",
            "description": "Consolidado mensual de pagos realizados al personal interno.",
            "columns": ["Mes", "Total pagado"],
            "rows": [
                [
                    item["periodo"].strftime("%m/%Y") if item["periodo"] else "Sin fecha",
                    _format_currency(item["total"] or 0),
                ]
                for item in registros
            ],
            "total_label": "Total general pagado",
            "total_value": _format_currency(
                _apply_date_range(PagoEmpleado.objects.all(), "fecha", fecha_desde, fecha_hasta).aggregate(total=Sum("monto"))["total"] or 0
            ),
        }

    if tipo_reporte == "pagos_empleados_por_metodo":
        registros = list(
            _apply_date_range(PagoEmpleado.objects.all(), "fecha", fecha_desde, fecha_hasta)
            .values("metodo")
            .annotate(total_pagado=Sum("monto"), cantidad=Count("id"))
            .order_by("metodo")
        )
        return {
            "title": "Pagos de empleados por metodo",
            "description": "Resumen de pagos de empleados por metodo de desembolso.",
            "columns": ["Metodo", "Cantidad", "Total pagado"],
            "rows": [
                [_choice_label(PagoEmpleado.Metodo.choices, item["metodo"]), item["cantidad"], _format_currency(item["total_pagado"] or 0)]
                for item in registros
            ],
            "total_label": "Total general pagado",
            "total_value": _format_currency(sum((item["total_pagado"] or 0) for item in registros)),
        }

    if tipo_reporte == "pagos_por_mes":
        registros = list(
            _apply_date_range(Pago.objects.all(), "fecha", fecha_desde, fecha_hasta)
            .annotate(periodo=TruncMonth("fecha"))
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
            "total_value": _format_currency(
                _apply_date_range(Pago.objects.all(), "fecha", fecha_desde, fecha_hasta).aggregate(total=Sum("monto"))["total"] or 0
            ),
        }

    if tipo_reporte == "pagos_por_metodo":
        registros = list(
            _apply_date_range(Pago.objects.all(), "fecha", fecha_desde, fecha_hasta)
            .values("metodo")
            .annotate(total_pagado=Sum("monto"), cantidad=Count("id"))
            .order_by("metodo")
        )
        return {
            "title": "Pagos a choferes por metodo",
            "description": "Resumen de pagos agrupados por metodo de desembolso.",
            "columns": ["Metodo", "Cantidad", "Total pagado"],
            "rows": [[_choice_label(Pago.Metodo.choices, item["metodo"]), item["cantidad"], _format_currency(item["total_pagado"] or 0)] for item in registros],
            "total_label": "Total general pagado",
            "total_value": _format_currency(sum((item["total_pagado"] or 0) for item in registros)),
        }

    if tipo_reporte == "productos_por_categoria":
        registros = list(
            Producto.objects.values("categoria")
            .annotate(total=Count("id"), stock=Sum("cantidad"))
            .order_by("categoria")
        )
        return {
            "title": "Productos por categoria",
            "description": "Clasificacion de inventario segun categoria de producto.",
            "columns": ["Categoria", "Productos", "Stock total"],
            "rows": [[_choice_label(Producto.Categoria.choices, item["categoria"]), item["total"], item["stock"] or 0] for item in registros],
            "total_label": "Productos registrados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "productos_activos":
        activos = Producto.objects.filter(activo=True).count()
        inactivos = Producto.objects.filter(activo=False).count()
        return {
            "title": "Productos activos e inactivos",
            "description": "Resumen del inventario segun disponibilidad operativa del producto.",
            "columns": ["Estado", "Cantidad"],
            "rows": [["Activos", activos], ["Inactivos", inactivos]],
            "total_label": "Productos contabilizados",
            "total_value": activos + inactivos,
        }

    if tipo_reporte == "movimientos_por_tipo":
        registros = list(
            _apply_date_range(MovimientoInventario.objects.all(), "fecha", fecha_desde, fecha_hasta)
            .values("tipo")
            .annotate(total=Count("id"), cantidad_total=Sum("cantidad"))
            .order_by("tipo")
        )
        return {
            "title": "Movimientos de inventario por tipo",
            "description": "Resumen de entradas, salidas y ajustes del inventario.",
            "columns": ["Tipo", "Movimientos", "Cantidad total"],
            "rows": [[_choice_label(MovimientoInventario.Tipo.choices, item["tipo"]), item["total"], item["cantidad_total"] or 0] for item in registros],
            "total_label": "Movimientos contabilizados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "suministros_por_estado_pago":
        registros = list(
            _apply_date_range(SuministroCombustible.objects.all(), "fecha", fecha_desde, fecha_hasta)
            .values("estado_pago")
            .annotate(total=Count("id"), monto_pendiente=Sum("saldo_pendiente"))
            .order_by("estado_pago")
        )
        return {
            "title": "Suministros por estado de pago",
            "description": "Resumen de despachos de combustible agrupados por estado de pago.",
            "columns": ["Estado de pago", "Cantidad", "Saldo pendiente"],
            "rows": [[_choice_label(SuministroCombustible.EstadoPago.choices, item["estado_pago"]), item["total"], _format_currency(item["monto_pendiente"] or 0)] for item in registros],
            "total_label": "Suministros contabilizados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "vehiculos_disponibles":
        registros = list(
            Vehiculo.objects.filter(estado=Vehiculo.Estado.DISPONIBLE)
            .order_by("placa")
            .values(
                "placa",
                "marca",
                "modelo",
                "ultima_ubicacion",
                "es_propiedad_empresa",
                "dueno_nombre",
            )
        )
        return {
            "title": "Vehiculos disponibles",
            "description": "Unidades actualmente disponibles para asignacion o servicio.",
            "columns": ["Placa", "Marca", "Modelo", "Ultima ubicacion", "Propiedad / dueno"],
            "rows": [
                [
                    item["placa"],
                    item["marca"] or "N/D",
                    item["modelo"],
                    item["ultima_ubicacion"] or "N/D",
                    "Empresa" if item["es_propiedad_empresa"] else f"Alquilado - {item['dueno_nombre'] or 'Dueno no especificado'}",
                ]
                for item in registros
            ],
            "total_label": "Vehiculos disponibles",
            "total_value": len(registros),
        }

    if tipo_reporte == "vehiculos_por_estado":
        registros = list(Vehiculo.objects.values("estado").annotate(total=Count("id")).order_by("estado"))
        return {
            "title": "Vehiculos por estado",
            "description": "Resumen de la flota segun el estado operativo de cada vehiculo.",
            "columns": ["Estado", "Cantidad"],
            "rows": [[_choice_label(Vehiculo.Estado.choices, item["estado"]), item["total"]] for item in registros],
            "total_label": "Vehiculos contabilizados",
            "total_value": sum(item["total"] for item in registros),
        }

    if tipo_reporte == "combustible_pendiente":
        registros = list(
            _apply_date_range(
                SuministroCombustible.objects.select_related("chofer", "producto", "vehiculo")
                .filter(saldo_pendiente__gt=0),
                "fecha",
                fecha_desde,
                fecha_hasta,
            )
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
                _apply_date_range(
                    SuministroCombustible.objects.filter(saldo_pendiente__gt=0),
                    "fecha",
                    fecha_desde,
                    fecha_hasta,
                ).aggregate(total=Sum("saldo_pendiente"))["total"] or 0
            ),
        }

    return None


def lista_reportes(request):
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

    return render(
        request,
        "reportes/lista_reportes.html",
        {
            "page_title": "Reportes",
            "page_intro": "Genera reportes operativos, financieros y de personal desde un solo panel.",
            "summary_cards": [
                {"label": "Choferes", "value": Chofer.objects.count(), "accent": "blue"},
                {"label": "Pagos choferes", "value": Pago.objects.count(), "accent": "green"},
                {"label": "Pagos empleados", "value": PagoEmpleado.objects.count(), "accent": "teal"},
                {"label": "Vehiculos", "value": Vehiculo.objects.count(), "accent": "amber"},
            ],
            "form": form,
            "selected_report": selected_report,
        },
    )
