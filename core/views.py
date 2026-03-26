from django.db.models import Sum
from django.shortcuts import render

from choferes.models import Chofer
from inventario.models import Producto
from pagos.models import Pago
from recursos_humanos.models import Capacitacion, Empleado, Licencia, PagoEmpleado, Vacacion
from reportes.models import Reporte
from tracking.models import Vehiculo


def dashboard(request):
    stock_total = Producto.objects.aggregate(total=Sum("cantidad"))["total"] or 0
    total_pagos_choferes = Pago.objects.aggregate(total=Sum("monto"))["total"] or 0
    total_pagos_empleados = PagoEmpleado.objects.aggregate(total=Sum("monto"))["total"] or 0

    context = {
        "page_title": "Centro de control",
        "page_intro": "Vista general operativa para flota, combustible, personal, pagos y control administrativo.",
        "summary_cards": [
            {"label": "Productos", "value": Producto.objects.count(), "accent": "teal"},
            {"label": "Unidades en stock", "value": stock_total, "accent": "amber"},
            {"label": "Choferes subcontratistas", "value": Chofer.objects.count(), "accent": "blue"},
            {"label": "Pagos choferes", "value": f"RD$ {total_pagos_choferes:,.2f}", "accent": "green"},
            {"label": "Pagos empleados", "value": f"RD$ {total_pagos_empleados:,.2f}", "accent": "amber"},
        ],
        "module_cards": [
            {
                "title": "Inventario",
                "text": "Control de productos, existencias y valor operativo del stock.",
                "metric": f"{stock_total} unidades disponibles",
                "href": "/inventario/",
            },
            {
                "title": "Gestion de choferes",
                "text": "Registro de choferes subcontratistas, conduces y pagos por servicio.",
                "metric": f"{Chofer.objects.count()} choferes y RD$ {total_pagos_choferes:,.2f} pagados",
                "href": "/choferes/",
            },
            {
                "title": "Recursos humanos",
                "text": "Empleados, pagos de empleados, licencias y vacaciones.",
                "metric": f"{Empleado.objects.count()} empleados y RD$ {total_pagos_empleados:,.2f} en pagos",
                "href": "/recursos_humanos/empleados/",
            },
            {
                "title": "Vehiculos",
                "text": "Registro y control operativo de la flota vehicular.",
                "metric": f"{Vehiculo.objects.count()} vehiculos registrados",
                "href": "/vehiculos/",
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
