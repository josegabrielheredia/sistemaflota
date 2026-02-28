from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.shortcuts import render

from .models import Producto


def lista_productos(request):
    productos = Producto.objects.all().order_by("nombre")
    total_unidades = productos.aggregate(total=Sum("cantidad"))["total"] or 0
    total_valor = productos.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("cantidad") * F("precio"),
                output_field=DecimalField(max_digits=14, decimal_places=2),
            )
        )
    )["total"] or 0

    return render(
        request,
        "inventario/lista_productos.html",
        {
            "page_title": "Inventario",
            "page_intro": "Control centralizado de productos, existencias y valor estimado del stock.",
            "summary_cards": [
                {"label": "Productos registrados", "value": productos.count(), "accent": "teal"},
                {"label": "Unidades disponibles", "value": total_unidades, "accent": "amber"},
                {"label": "Valor estimado", "value": f"RD$ {total_valor:,.2f}", "accent": "green"},
            ],
            "productos": productos,
        },
    )
