from django.shortcuts import render

from .models import Reporte


def lista_reportes(request):
    reportes = Reporte.objects.all().order_by("-fecha", "-id")
    return render(
        request,
        "reportes/lista_reportes.html",
        {
            "page_title": "Reportes",
            "page_intro": "Consolidado documental de hallazgos, novedades e incidencias del sistema.",
            "summary_cards": [
                {"label": "Reportes emitidos", "value": reportes.count(), "accent": "green"},
            ],
            "reportes": reportes,
        },
    )
