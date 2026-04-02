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
                ("choferes_licencias_por_vencimiento", "Licencias de choferes por vencimiento"),
                ("choferes_rntt_por_vencimiento", "Carnet RNTT por vencimiento"),
                ("choferes_seguro_ley_por_vencimiento", "Seguro de ley por vencimiento"),
                ("conduces_listado", "Listado de conduces"),
            ],
        ),
        (
            "Recursos humanos",
            [
                ("empleados_activos", "Empleados activos"),
                ("empleados_por_estado", "Empleados por estado"),
                ("empleados_por_departamento", "Empleados por departamento"),
                ("empleados_por_cumpleanos", "Empleados por fecha de cumpleanos"),
                ("gastos_rrhh_listado", "Todos los gastos (listado)"),
                ("gastos_rrhh_por_proveedor", "Gastos por proveedor"),
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
            "Pagos y combustible a choferes",
            [
                ("pagos_por_mes", "Total pagado a choferes por mes"),
                ("pagos_por_metodo", "Pagos a choferes por metodo"),
                ("suministros_combustible_por_estado", "Suministros de combustible por estado"),
                ("saldo_combustible_pendiente", "Saldo pendiente por combustible suministrado por adelantado"),
                ("cobros_combustible_por_mes", "Cobros de combustible por mes"),
            ],
        ),
        (
            "Inventario",
            [
                ("productos_por_categoria", "Productos por categoria"),
                ("productos_activos", "Productos activos e inactivos"),
                ("movimientos_por_tipo", "Movimientos de inventario por tipo"),
            ],
        ),
        (
            "Vehiculos y contenedores",
            [
                ("vehiculos_disponibles", "Vehiculos disponibles"),
                ("vehiculos_por_estado", "Vehiculos por estado"),
                ("contenedores_disponibles", "Contenedores disponibles"),
                ("contenedores_por_estado", "Contenedores por estado"),
                ("contenedores_alquilados", "Contenedores alquilados"),
            ],
        ),
        (
            "Proveedores",
            [
                ("registros_proveedores_por_empresa", "Registros de proveedores por empresa"),
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
