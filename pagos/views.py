from django.db.models import Sum
from django.shortcuts import render

from .models import Pago


def lista_pagos(request):
    pagos = Pago.objects.select_related("chofer").order_by("-fecha", "-id")
    total_pagado = pagos.aggregate(total=Sum("monto"))["total"] or 0
    return render(
        request,
        "pagos/lista_pagos.html",
        {
            "page_title": "Pagos",
            "page_intro": "Registro financiero de pagos realizados a choferes con metodo y fecha de ejecucion.",
            "summary_cards": [
                {"label": "Pagos registrados", "value": pagos.count(), "accent": "green"},
                {"label": "Monto total", "value": f"RD$ {total_pagado:,.2f}", "accent": "amber"},
            ],
            "pagos": pagos,
        },
    )
