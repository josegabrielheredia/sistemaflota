from django import forms


class GeneradorReporteForm(forms.Form):
    REPORTE_CHOICES = [
        ("choferes_registrados", "Choferes subcontratistas registrados"),
        ("empleados_activos", "Empleados activos"),
        ("licencias_activas", "Licencias activas"),
        ("vacaciones_activas", "Vacaciones activas"),
        ("pagos_por_mes", "Total pagado a choferes por mes"),
        ("vehiculos_disponibles", "Vehiculos disponibles"),
        ("cuentas_pendientes", "Cuentas pendientes"),
        ("combustible_pendiente", "Suministros de combustible pendientes"),
    ]

    tipo_reporte = forms.ChoiceField(
        choices=REPORTE_CHOICES,
        label="Generar reporte",
        widget=forms.Select(attrs={"class": "site-input site-select"}),
    )
