from django.shortcuts import render

from .models import Chofer


def lista_choferes(request):
    choferes = Chofer.objects.all().order_by("nombre")
    return render(
        request,
        "choferes/lista_choferes.html",
        {
            "page_title": "Choferes",
            "page_intro": "Directorio operativo del personal de conduccion y sus credenciales principales.",
            "summary_cards": [
                {"label": "Choferes registrados", "value": choferes.count(), "accent": "blue"},
                {"label": "Licencias cargadas", "value": choferes.exclude(licencia="").count(), "accent": "teal"},
            ],
            "choferes": choferes,
        },
    )
