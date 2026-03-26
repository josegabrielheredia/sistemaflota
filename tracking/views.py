from django.shortcuts import render

from .models import Vehiculo


def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.all().order_by("placa")
    return render(
        request,
        "tracking/lista_vehiculos.html",
        {
            "page_title": "Vehiculos",
            "page_intro": "Registro y control operativo de vehiculos propios o alquilados para servicio.",
            "summary_cards": [
                {"label": "Vehiculos registrados", "value": vehiculos.count(), "accent": "blue"},
                {"label": "Vehiculos de la empresa", "value": vehiculos.filter(es_propiedad_empresa=True).count(), "accent": "teal"},
                {"label": "Vehiculos alquilados", "value": vehiculos.filter(es_propiedad_empresa=False).count(), "accent": "amber"},
            ],
            "vehiculos": vehiculos,
        },
    )
