from django import forms

from .models import RegistroGasto


class RegistroGastoForm(forms.ModelForm):
    class Meta:
        model = RegistroGasto
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha"].widget = forms.DateInput(
            attrs={"class": "vDateField", "type": "date"}
        )
        self.fields["numero_comprobante"].help_text = (
            "Solo requerido cuando el gasto es con comprobante."
        )
        self.fields["propinas"].help_text = "Opcional, si aplica."

