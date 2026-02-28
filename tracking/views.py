from django.shortcuts import render

from .models import Vehiculo


def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.all().order_by("placa")
    return render(
        request,
        "tracking/lista_vehiculos.html",
        {
            "page_title": "Tracking",
            "page_intro": "Monitoreo de ubicacion y trazabilidad operativa de la flota.",
            "summary_cards": [
                {"label": "Vehiculos monitoreados", "value": vehiculos.count(), "accent": "blue"},
                {"label": "Con ubicacion reportada", "value": vehiculos.exclude(ultima_ubicacion="").count(), "accent": "teal"},
            ],
            "vehiculos": vehiculos,
        },
    )
