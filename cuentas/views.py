from django.db.models import Sum
from django.shortcuts import render

from .models import Cuenta


def lista_cuentas(request):
    cuentas = Cuenta.objects.all().order_by("fecha_vencimiento", "nombre")
    total_monto = cuentas.aggregate(total=Sum("monto"))["total"] or 0
    return render(
        request,
        "cuentas/lista_cuentas.html",
        {
            "page_title": "Cuentas",
            "page_intro": "Seguimiento de compromisos financieros y cobros pendientes con enfoque en vencimientos.",
            "summary_cards": [
                {"label": "Cuentas totales", "value": cuentas.count(), "accent": "blue"},
                {"label": "Por pagar", "value": cuentas.filter(tipo__iexact="Pagar").count(), "accent": "amber"},
                {"label": "Por cobrar", "value": cuentas.filter(tipo__iexact="Cobrar").count(), "accent": "teal"},
                {"label": "Monto comprometido", "value": f"RD$ {total_monto:,.2f}", "accent": "green"},
            ],
            "cuentas": cuentas,
        },
    )
