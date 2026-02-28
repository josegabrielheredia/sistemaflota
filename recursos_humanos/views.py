from django.shortcuts import render

from .models import Capacitacion, Empleado, Licencia, Vacacion


def lista_empleados(request):
    empleados = Empleado.objects.all().order_by("nombre")
    return render(
        request,
        "recursos_humanos/lista_empleados.html",
        {
            "page_title": "Recursos humanos",
            "page_intro": "Gestion del talento, historial laboral y programacion de desarrollo interno.",
            "summary_cards": [
                {"label": "Empleados", "value": empleados.count(), "accent": "blue"},
                {"label": "Licencias activas", "value": Licencia.objects.count(), "accent": "amber"},
                {"label": "Vacaciones", "value": Vacacion.objects.count(), "accent": "teal"},
                {"label": "Capacitaciones", "value": Capacitacion.objects.count(), "accent": "green"},
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
            "licencias": Licencia.objects.select_related("empleado").order_by("-fecha_inicio"),
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
            "vacaciones": Vacacion.objects.select_related("empleado").order_by("-fecha_inicio"),
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
            "capacitaciones": Capacitacion.objects.select_related("empleado").order_by("-fecha"),
            "rrhh_section": "capacitaciones",
        },
    )
