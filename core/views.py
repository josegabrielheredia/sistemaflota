from django.db.models import Sum
from django.shortcuts import render

from choferes.models import Chofer
from cuentas.models import Cuenta
from inventario.models import Producto
from pagos.models import Pago
from recursos_humanos.models import Capacitacion, Empleado, Licencia, Vacacion
from reportes.models import Reporte
from tracking.models import Vehiculo


def dashboard(request):
    stock_total = Producto.objects.aggregate(total=Sum("cantidad"))["total"] or 0
    total_pagos = Pago.objects.aggregate(total=Sum("monto"))["total"] or 0

    context = {
        "page_title": "Centro de control",
        "page_intro": "Vista general operativa para flota, combustible, personal, pagos y control administrativo.",
        "summary_cards": [
            {"label": "Productos", "value": Producto.objects.count(), "accent": "teal"},
            {"label": "Unidades en stock", "value": stock_total, "accent": "amber"},
            {"label": "Choferes activos", "value": Chofer.objects.count(), "accent": "blue"},
            {"label": "Pagos registrados", "value": f"RD$ {total_pagos:,.2f}", "accent": "green"},
        ],
        "module_cards": [
            {
                "title": "Inventario",
                "text": "Control de productos, existencias y valor operativo del stock.",
                "metric": f"{stock_total} unidades disponibles",
                "href": "/inventario/",
            },
            {
                "title": "Choferes",
                "text": "Base operativa del personal de conduccion y sus licencias.",
                "metric": f"{Chofer.objects.count()} choferes registrados",
                "href": "/choferes/",
            },
            {
                "title": "Pagos",
                "text": "Seguimiento financiero de desembolsos a choferes.",
                "metric": f"RD$ {total_pagos:,.2f} procesados",
                "href": "/pagos/",
            },
            {
                "title": "Cuentas",
                "text": "Cuentas por pagar y por cobrar con foco en vencimientos.",
                "metric": f"{Cuenta.objects.count()} cuentas en seguimiento",
                "href": "/cuentas/",
            },
            {
                "title": "Recursos humanos",
                "text": "Empleados, licencias, vacaciones y capacitaciones.",
                "metric": f"{Empleado.objects.count()} empleados",
                "href": "/recursos_humanos/empleados/",
            },
            {
                "title": "Tracking",
                "text": "Ubicacion operativa y trazabilidad de la flota.",
                "metric": f"{Vehiculo.objects.count()} vehiculos monitoreados",
                "href": "/tracking/",
            },
            {
                "title": "Reportes",
                "text": "Consolidado de novedades, hallazgos e incidencias.",
                "metric": f"{Reporte.objects.count()} reportes generados",
                "href": "/reportes/",
            },
            {
                "title": "Licencias",
                "text": "Seguimiento de licencias, vacaciones y novedades del personal.",
                "metric": f"{Licencia.objects.count()} licencias y {Vacacion.objects.count()} vacaciones registradas",
                "href": "/recursos_humanos/licencias/",
            },
        ],
        "recent_payments": Pago.objects.select_related("chofer").order_by("-fecha", "-id")[:5],
        "recent_reports": Reporte.objects.order_by("-fecha", "-id")[:5],
    }
    return render(request, "dashboard.html", context)
