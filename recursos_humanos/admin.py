from django.contrib import admin

from .models import Capacitacion, Cargo, Departamento, Empleado, Licencia, PagoEmpleado, TipoLicencia, Vacacion


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "departamento")
    search_fields = ("nombre", "departamento__nombre")


class LicenciaInline(admin.TabularInline):
    model = Licencia
    extra = 0


class VacacionInline(admin.TabularInline):
    model = Vacacion
    extra = 0


class CapacitacionInline(admin.TabularInline):
    model = Capacitacion
    extra = 0


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "cedula", "departamento", "designacion", "estado")
    search_fields = ("nombre", "apellidos", "cedula", "telefono", "correo")
    inlines = [LicenciaInline, VacacionInline, CapacitacionInline]

    @admin.display(description="Empleado")
    def nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellidos}".strip()

    @admin.display(description="Departamento")
    def departamento(self, obj):
        return obj.cargo.departamento.nombre

    @admin.display(description="Designacion")
    def designacion(self, obj):
        return obj.cargo.nombre


@admin.register(TipoLicencia)
class TipoLicenciaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "requiere_aprobacion", "activo")
    search_fields = ("nombre",)


@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tipo", "fecha_inicio", "fecha_fin", "estado")
    search_fields = ("empleado__nombre", "tipo__nombre", "motivo")


@admin.register(Vacacion)
class VacacionAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha_inicio", "fecha_fin", "estado")
    search_fields = ("empleado__nombre",)


@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tema", "fecha_inicio", "fecha_fin", "proveedor")
    search_fields = ("empleado__nombre", "tema", "proveedor")


@admin.register(PagoEmpleado)
class PagoEmpleadoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha", "monto", "metodo", "referencia")
    search_fields = ("empleado__nombre", "empleado__apellidos", "empleado__cedula", "referencia")
