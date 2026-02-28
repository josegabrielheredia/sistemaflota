from django.contrib import admin

from .models import Capacitacion, Cargo, Departamento, Empleado, Licencia, TipoLicencia, Vacacion


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "departamento")
    list_filter = ("departamento",)
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
    list_display = ("nombre", "cedula", "cargo", "fecha_ingreso", "estado")
    list_filter = ("estado", "cargo__departamento", "cargo")
    search_fields = ("nombre", "cedula", "telefono", "correo")
    inlines = [LicenciaInline, VacacionInline, CapacitacionInline]


@admin.register(TipoLicencia)
class TipoLicenciaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "requiere_aprobacion", "activo")
    list_filter = ("requiere_aprobacion", "activo")
    search_fields = ("nombre",)


@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tipo", "fecha_inicio", "fecha_fin", "estado")
    list_filter = ("estado", "tipo")
    search_fields = ("empleado__nombre", "tipo__nombre", "motivo")


@admin.register(Vacacion)
class VacacionAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha_inicio", "fecha_fin", "estado")
    list_filter = ("estado",)
    search_fields = ("empleado__nombre",)


@admin.register(Capacitacion)
class CapacitacionAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tema", "fecha", "proveedor", "horas")
    search_fields = ("empleado__nombre", "tema", "proveedor")
