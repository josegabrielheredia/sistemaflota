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
    seguro_ley = forms.TypedChoiceField(
        label="Seguro de ley",
        choices=((True, "Si"), (False, "No")),
        coerce=lambda value: value in [True, "True", "true", "1", 1, "Si", "si"],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Chofer
        fields = [
            "cedula",
            "licencia",
            "categoria_licencia",
            "vencimiento_licencia",
            "carta_buena_conducta",
            "rntt",
            "vencimiento_carnet_rntt",
            "seguro_ley",
            "vencimiento_seguro_ley",
        ]
        labels = {
            "cedula": "Cedula",
            "licencia": "Numero de licencia",
            "categoria_licencia": "Categoria de licencia",
            "vencimiento_licencia": "Vencimiento de licencia",
            "carta_buena_conducta": "Carta de buena conducta",
            "rntt": "RNTT",
            "vencimiento_carnet_rntt": "Vencimiento carnet RNTT",
            "seguro_ley": "Seguro de ley",
            "vencimiento_seguro_ley": "Vencimiento seguro de ley",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_fields(
            [
                "nombres",
                "apellidos",
                "cedula",
                "licencia",
                "categoria_licencia",
                "vencimiento_licencia",
                "carta_buena_conducta",
                "rntt",
                "vencimiento_carnet_rntt",
                "seguro_ley",
                "vencimiento_seguro_ley",
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
            "categoria_licencia": "Ej. Categoria 3",
        }
        for name, field in self.fields.items():
            css = "site-input"
            if isinstance(field.widget, forms.Textarea):
                css = "site-input site-textarea"
            elif isinstance(field.widget, forms.Select):
                css = "site-input site-select"
            elif isinstance(field.widget, forms.DateInput):
                css = "site-input"
            field.widget.attrs["class"] = css
            if name in placeholders:
                field.widget.attrs["placeholder"] = placeholders[name]

        for field_name in (
            "vencimiento_licencia",
            "vencimiento_carnet_rntt",
            "vencimiento_seguro_ley",
        ):
            if field_name in self.fields:
                self.fields[field_name].widget = forms.DateInput(
                    attrs={"class": "site-input", "type": "date"}
                )

        if "class" not in self.fields["carta_buena_conducta"].widget.attrs:
            self.fields["carta_buena_conducta"].widget.attrs["class"] = "inline-radio-list"
        if "class" not in self.fields["rntt"].widget.attrs:
            self.fields["rntt"].widget.attrs["class"] = "inline-radio-list"
        if "class" not in self.fields["seguro_ley"].widget.attrs:
            self.fields["seguro_ley"].widget.attrs["class"] = "inline-radio-list"

    def save(self, commit=True):
        instance = super().save(commit=False)
        nombres = (self.cleaned_data.get("nombres") or "").strip()
        apellidos = (self.cleaned_data.get("apellidos") or "").strip()
        instance.nombre = f"{nombres} {apellidos}".strip()
        if commit:
            instance.save()
        return instance
