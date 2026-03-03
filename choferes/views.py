from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ChoferSubcontratistaForm
from .models import Chofer


def lista_choferes(request):
    choferes = Chofer.objects.all().order_by("nombre")
    return render(
        request,
        "choferes/lista_choferes.html",
        {
            "page_title": "Choferes subcontratistas",
            "page_intro": "Registro operativo de choferes contratados por servicio, con su documentacion y credenciales principales.",
            "summary_cards": [
                {"label": "Choferes registrados", "value": choferes.count(), "accent": "blue"},
                {"label": "Licencias cargadas", "value": choferes.exclude(licencia="").count(), "accent": "teal"},
                {"label": "Pago por transferencia", "value": choferes.filter(metodo_pago_preferido=Chofer.MetodoPago.TRANSFERENCIA).count(), "accent": "green"},
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
            "page_title": "Registrar chofer subcontratista",
            "page_intro": "Completa el formulario operativo del subcontratista para poder asignarle conduces y pagos por servicio.",
            "form": form,
        },
    )
