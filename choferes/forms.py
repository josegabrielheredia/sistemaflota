from django import forms

from .models import Chofer


class ChoferSubcontratistaForm(forms.ModelForm):
    nombres = forms.CharField(max_length=100, label="Nombres")
    apellidos = forms.CharField(max_length=100, label="Apellidos")
    carta_buena_conducta = forms.TypedChoiceField(
        label="Carta de buena conducta",
        choices=((True, "Si"), (False, "No")),
        coerce=lambda value: value in [True, "True", "true", "1", 1, "Si", "si"],
        widget=forms.RadioSelect,
    )
    rntt = forms.TypedChoiceField(
        label="RNTT",
        choices=((True, "Si"), (False, "No")),
        coerce=lambda value: value in [True, "True", "true", "1", 1, "Si", "si"],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Chofer
        fields = [
            "cedula",
            "licencia",
            "carta_buena_conducta",
            "rntt",
        ]
        labels = {
            "cedula": "Cedula",
            "licencia": "Numero de licencia",
            "carta_buena_conducta": "Carta de buena conducta",
            "rntt": "RNTT",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(
            [
                "nombres",
                "apellidos",
                "cedula",
                "licencia",
                "carta_buena_conducta",
                "rntt",
            ]
        )

        if self.instance and self.instance.pk and self.instance.nombre:
            partes = self.instance.nombre.split()
            if len(partes) == 1:
                self.fields["nombres"].initial = partes[0]
            else:
                self.fields["nombres"].initial = partes[0]
                self.fields["apellidos"].initial = " ".join(partes[1:])

        placeholders = {
            "nombres": "Ej. Juan Carlos",
            "apellidos": "Ej. Perez Ramirez",
            "cedula": "000-0000000-0",
            "licencia": "Numero de licencia vigente",
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

        if "class" not in self.fields["carta_buena_conducta"].widget.attrs:
            self.fields["carta_buena_conducta"].widget.attrs["class"] = "inline-radio-list"
        if "class" not in self.fields["rntt"].widget.attrs:
            self.fields["rntt"].widget.attrs["class"] = "inline-radio-list"

    def save(self, commit=True):
        instance = super().save(commit=False)
        nombres = (self.cleaned_data.get("nombres") or "").strip()
        apellidos = (self.cleaned_data.get("apellidos") or "").strip()
        instance.nombre = f"{nombres} {apellidos}".strip()
        if commit:
            instance.save()
        return instance
