from datetime import date, timedelta

from django.db.models import Sum
from django.shortcuts import render

from .models import Capacitacion, Empleado, Licencia, PagoEmpleado, RegistroGasto, Vacacion


def _cumpleanos_en_anio(fecha_nacimiento, anio):
    if not fecha_nacimiento:
        return None
    try:
        return fecha_nacimiento.replace(year=anio)
    except ValueError:
        return date(anio, 2, 28)


def _proximo_cumpleanos(fecha_nacimiento, referencia=None):
    referencia = referencia or date.today()
    cumple_este_anio = _cumpleanos_en_anio(fecha_nacimiento, referencia.year)
    if not cumple_este_anio:
        return None
    if cumple_este_anio < referencia:
        return _cumpleanos_en_anio(fecha_nacimiento, referencia.year + 1)
    return cumple_este_anio


def lista_empleados(request):
    Vacacion.sincronizar_estados()
    empleados = Empleado.objects.select_related("cargo", "cargo__departamento").order_by("nombre")
    total_pagos = PagoEmpleado.objects.aggregate(total=Sum("monto"))["total"] or 0
    hoy = date.today()
    proximos_cumpleanos = []
    for empleado in empleados:
        if not empleado.fecha_nacimiento:
            continue
        proximo = _proximo_cumpleanos(empleado.fecha_nacimiento, hoy)
        if not proximo:
            continue
        dias_restantes = (proximo - hoy).days
        if 0 <= dias_restantes <= 7:
            proximos_cumpleanos.append(
                {
                    "empleado": empleado,
                    "proximo_cumpleanos": proximo,
                    "dias_restantes": dias_restantes,
                }
            )

    proximos_cumpleanos.sort(
        key=lambda item: (item["dias_restantes"], item["empleado"].nombre.lower())
    )
    return render(
        request,
        "recursos_humanos/lista_empleados.html",
        {
            "page_title": "Recursos humanos",
            "page_intro": "Gestion del personal interno, pagos de empleados y seguimiento de ausencias.",
            "summary_cards": [
                {"label": "Empleados", "value": empleados.count(), "accent": "blue"},
                {"label": "Pagos empleados", "value": f"RD$ {total_pagos:,.2f}", "accent": "green"},
                {
                    "label": "Licencias activas",
                    "value": Licencia.objects.filter(estado=Licencia.Estado.ACTIVA).count(),
                    "accent": "amber",
                },
                {"label": "Vacaciones en curso", "value": Vacacion.objects.filter(estado=Vacacion.Estado.EN_CURSO).count(), "accent": "teal"},
                {
                    "label": "Cumpleanos proximos (7 dias)",
                    "value": len(proximos_cumpleanos),
                    "accent": "blue",
                },
            ],
            "empleados": empleados,
            "proximos_cumpleanos": proximos_cumpleanos,
            "rrhh_section": "empleados",
        },
    )


def lista_licencias(request):
    return render(
        request,
        "recursos_humanos/lista_licencias.html",
        {
            "page_title": "Licencias",
            "page_intro": "Historial y seguimiento de licencias por colaborador.",
            "licencias": Licencia.objects.select_related("empleado", "tipo").order_by("-fecha_inicio"),
            "rrhh_section": "licencias",
        },
    )


def lista_vacaciones(request):
    Vacacion.sincronizar_estados()
    return render(
        request,
        "recursos_humanos/lista_vacaciones.html",
        {
            "page_title": "Vacaciones",
            "page_intro": "Planificacion de descanso y control de ausencias programadas.",
            "vacaciones": Vacacion.objects.select_related("empleado", "empleado__cargo").order_by("-fecha_inicio"),
            "rrhh_section": "vacaciones",
        },
    )


def lista_capacitaciones(request):
    return render(
        request,
        "recursos_humanos/lista_capacitaciones.html",
        {
            "page_title": "Capacitaciones",
            "page_intro": "Formacion y desarrollo de capacidades del equipo.",
            "capacitaciones": Capacitacion.objects.select_related(
                "empleado",
                "empleado__cargo",
                "empleado__cargo__departamento",
            ).order_by("-fecha_inicio"),
            "rrhh_section": "capacitaciones",
        },
    )


def lista_pagos_empleados(request):
    pagos = PagoEmpleado.objects.select_related("empleado", "empleado__cargo", "empleado__cargo__departamento").order_by("-fecha", "-id")
    total_pagado = pagos.aggregate(total=Sum("monto"))["total"] or 0
    return render(
        request,
        "recursos_humanos/lista_pagos.html",
        {
            "page_title": "Pagos de empleados",
            "page_intro": "Registro de pagos correspondientes al personal interno de la empresa.",
            "summary_cards": [
                {"label": "Pagos registrados", "value": pagos.count(), "accent": "green"},
                {"label": "Monto total", "value": f"RD$ {total_pagado:,.2f}", "accent": "amber"},
            ],
            "pagos": pagos,
            "rrhh_section": "pagos",
        },
    )


def lista_gastos_rrhh(request):
    gastos = RegistroGasto.objects.order_by("-fecha", "-id")
    total_valor = gastos.aggregate(total=Sum("valor"))["total"] or 0
    total_itbis = gastos.aggregate(total=Sum("itbis"))["total"] or 0
    total_propinas = gastos.aggregate(total=Sum("propinas"))["total"] or 0
    total_general = total_valor + total_itbis + total_propinas
    return render(
        request,
        "recursos_humanos/lista_gastos.html",
        {
            "page_title": "Registros de gastos",
            "page_intro": "Control de gastos operativos y administrativos del area de recursos humanos.",
            "summary_cards": [
                {"label": "Gastos registrados", "value": gastos.count(), "accent": "blue"},
                {"label": "Total valor", "value": f"RD$ {total_valor:,.2f}", "accent": "teal"},
                {"label": "Total ITBIS", "value": f"RD$ {total_itbis:,.2f}", "accent": "amber"},
                {"label": "Total general", "value": f"RD$ {total_general:,.2f}", "accent": "green"},
            ],
            "gastos": gastos,
            "rrhh_section": "gastos",
        },
    )
