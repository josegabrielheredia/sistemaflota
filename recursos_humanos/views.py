from django.db.models import Sum
from django.shortcuts import render

from .models import Capacitacion, Empleado, Licencia, PagoEmpleado, Vacacion


def lista_empleados(request):
    empleados = Empleado.objects.select_related("cargo", "cargo__departamento").order_by("nombre")
    total_pagos = PagoEmpleado.objects.aggregate(total=Sum("monto"))["total"] or 0
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
            ],
            "empleados": empleados,
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
