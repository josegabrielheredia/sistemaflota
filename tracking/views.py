from django.shortcuts import render

from .models import Vehiculo


def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.all().order_by("placa")
    return render(
        request,
        "tracking/lista_vehiculos.html",
        {
            "page_title": "Vehiculos",
            "page_intro": "Registro y control operativo de vehiculos disponibles para servicio.",
            "summary_cards": [
                {"label": "Vehiculos registrados", "value": vehiculos.count(), "accent": "blue"},
                {"label": "Vehiculos disponibles", "value": vehiculos.filter(estado=Vehiculo.Estado.DISPONIBLE).count(), "accent": "teal"},
            ],
            "vehiculos": vehiculos,
        },
    )
