from django import forms

from .models import Chofer


class ChoferSubcontratistaForm(forms.ModelForm):
    class Meta:
        model = Chofer
        fields = [
            "nombre",
            "cedula",
            "telefono",
            "direccion",
            "licencia",
            "categoria_licencia",
            "vencimiento_licencia",
            "metodo_pago_preferido",
            "banco",
            "titular_cuenta",
            "numero_cuenta",
            "honorario_referencial",
            "estado",
            "observaciones",
        ]
        widgets = {
            "vencimiento_licencia": forms.DateInput(attrs={"type": "date"}),
            "direccion": forms.Textarea(attrs={"rows": 3}),
            "observaciones": forms.Textarea(attrs={"rows": 4}),
            "honorario_referencial": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }
        labels = {
            "nombre": "Nombre completo",
            "cedula": "Cedula",
            "telefono": "Telefono principal",
            "direccion": "Direccion",
            "licencia": "Numero de licencia",
            "categoria_licencia": "Categoria de licencia",
            "vencimiento_licencia": "Vencimiento de licencia",
            "metodo_pago_preferido": "Metodo de pago preferido",
            "banco": "Banco",
            "titular_cuenta": "Titular de cuenta o beneficiario",
            "numero_cuenta": "Numero de cuenta",
            "honorario_referencial": "Honorario referencial por servicio",
            "estado": "Estado operativo",
            "observaciones": "Observaciones",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "nombre": "Ej. Juan Perez Ramirez",
            "cedula": "000-0000000-0",
            "telefono": "809-000-0000",
            "direccion": "Direccion base del subcontratista",
            "licencia": "Numero de licencia vigente",
            "categoria_licencia": "Ej. Categoria 4",
            "banco": "Banco de preferencia",
            "titular_cuenta": "Nombre del beneficiario",
            "numero_cuenta": "Cuenta o identificador bancario",
            "honorario_referencial": "Monto estimado por servicio",
            "observaciones": "Notas del expediente, disponibilidad o condiciones del servicio",
        }
        for name, field in self.fields.items():
            css = "site-input"
            if isinstance(field.widget, forms.Textarea):
                css = "site-input site-textarea"
            elif isinstance(field.widget, forms.Select):
                css = "site-input site-select"
            field.widget.attrs["class"] = css
            if name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[name]

    def clean(self):
        cleaned_data = super().clean()
        metodo = cleaned_data.get("metodo_pago_preferido")
        banco = (cleaned_data.get("banco") or "").strip()
        titular = (cleaned_data.get("titular_cuenta") or "").strip()
        cuenta = (cleaned_data.get("numero_cuenta") or "").strip()

        if metodo == Chofer.MetodoPago.TRANSFERENCIA:
            if not banco:
                self.add_error("banco", "Indica el banco para transferencias.")
            if not titular:
                self.add_error("titular_cuenta", "Indica el titular de la cuenta.")
            if not cuenta:
                self.add_error("numero_cuenta", "Indica el numero de cuenta para transferencias.")

        if metodo == Chofer.MetodoPago.CHEQUE and not titular:
            self.add_error("titular_cuenta", "Indica el beneficiario del cheque.")

        return cleaned_data
