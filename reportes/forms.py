from django import forms


class GeneradorReporteForm(forms.Form):
    REPORTE_CHOICES = [
        (
            "Choferes y conduces",
            [
                ("choferes_registrados", "Choferes subcontratistas registrados"),
                ("choferes_por_estado", "Choferes por estado"),
                ("choferes_carta_buena_conducta", "Choferes por carta de buena conducta"),
                ("choferes_rntt", "Choferes por cumplimiento de RNTT"),
                ("conduces_por_estado", "Conduces por estado"),
            ],
        ),
        (
            "Recursos humanos",
            [
                ("empleados_activos", "Empleados activos"),
                ("empleados_por_estado", "Empleados por estado"),
                ("empleados_por_departamento", "Empleados por departamento"),
                ("pagos_empleados_por_mes", "Pagos de empleados por mes"),
                ("pagos_empleados_por_metodo", "Pagos de empleados por metodo"),
                ("licencias_activas", "Licencias activas"),
                ("licencias_por_estado", "Licencias por estado"),
                ("tipos_licencia_configurados", "Tipos de licencia configurados"),
                ("vacaciones_activas", "Vacaciones activas"),
                ("vacaciones_por_estado", "Vacaciones por estado"),
            ],
        ),
        (
            "Pagos a choferes",
            [
                ("pagos_por_mes", "Total pagado a choferes por mes"),
                ("pagos_por_metodo", "Pagos a choferes por metodo"),
            ],
        ),
        (
            "Inventario y combustible",
            [
                ("productos_por_categoria", "Productos por categoria"),
                ("productos_activos", "Productos activos e inactivos"),
                ("movimientos_por_tipo", "Movimientos de inventario por tipo"),
                ("suministros_por_estado_pago", "Suministros de combustible por estado de pago"),
                ("combustible_pendiente", "Suministros de combustible pendientes"),
            ],
        ),
        (
            "Flota",
            [
                ("vehiculos_disponibles", "Vehiculos disponibles"),
                ("vehiculos_por_estado", "Vehiculos por estado"),
            ],
        ),
    ]

    tipo_reporte = forms.ChoiceField(
        choices=REPORTE_CHOICES,
        label="Generar reporte",
        widget=forms.Select(attrs={"class": "site-input site-select"}),
    )
    fecha_desde = forms.DateField(
        required=False,
        label="Desde",
        widget=forms.DateInput(attrs={"class": "site-input", "type": "date"}),
    )
    fecha_hasta = forms.DateField(
        required=False,
        label="Hasta",
        widget=forms.DateInput(attrs={"class": "site-input", "type": "date"}),
    )

    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get("fecha_desde")
        fecha_hasta = cleaned_data.get("fecha_hasta")
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise forms.ValidationError("La fecha inicial no puede ser mayor que la fecha final.")
        return cleaned_data
