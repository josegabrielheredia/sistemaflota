from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect, render

from .forms import ChoferSubcontratistaForm
from .models import Chofer
from pagos.models import Pago


def lista_choferes(request):
    choferes = Chofer.objects.all().order_by("nombre")
    return render(
        request,
        "choferes/lista_choferes.html",
        {
            "page_title": "Gestion de choferes",
            "page_intro": "Registro de choferes subcontratistas y control de pagos por servicio.",
            "summary_cards": [
                {"label": "Choferes registrados", "value": choferes.count(), "accent": "blue"},
                {"label": "Licencias cargadas", "value": choferes.exclude(licencia="").count(), "accent": "teal"},
                {"label": "Carta de buena conducta", "value": choferes.filter(carta_buena_conducta=True).count(), "accent": "green"},
                {"label": "RNTT cumplido", "value": choferes.filter(rntt=True).count(), "accent": "amber"},
            ],
            "choferes": choferes,
        },
    )


def registrar_chofer(request):
    if request.method == "POST":
        form = ChoferSubcontratistaForm(request.POST)
        if form.is_valid():
            chofer = form.save()
            messages.success(request, f"Chofer subcontratista '{chofer.nombre}' registrado correctamente.")
            return redirect("lista_choferes")
    else:
        form = ChoferSubcontratistaForm()

    return render(
        request,
        "choferes/registrar_chofer.html",
        {
            "page_title": "Gestion de choferes",
            "page_intro": "Registro de choferes subcontratistas con requisitos internos de la empresa.",
            "form": form,
        },
    )


def lista_pagos_choferes(request):
    pagos = Pago.objects.select_related("chofer", "conduce", "registrado_por").order_by("-fecha", "-id")
    total_pagado = pagos.aggregate(total=Sum("monto"))["total"] or 0
    return render(
        request,
        "pagos/lista_pagos.html",
        {
            "page_title": "Gestion de choferes",
            "page_intro": "Pagos a choferes por servicio, con su conduce y metodo de desembolso.",
            "summary_cards": [
                {"label": "Pagos registrados", "value": pagos.count(), "accent": "green"},
                {"label": "Monto total pagado", "value": f"RD$ {total_pagado:,.2f}", "accent": "amber"},
            ],
            "pagos": pagos,
        },
    )
