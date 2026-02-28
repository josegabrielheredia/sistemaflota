from django.db import migrations


def seed_tipos_licencia(apps, schema_editor):
    TipoLicencia = apps.get_model("recursos_humanos", "TipoLicencia")
    defaults = [
        ("Vacaciones", "Descanso programado del empleado."),
        ("Licencia medica", "Ausencia por indicacion medica."),
        ("Maternidad", "Licencia por maternidad."),
        ("Paternidad", "Licencia por paternidad."),
        ("Permiso especial", "Permiso autorizado por administracion."),
        ("Suspension", "Suspension temporal del empleado."),
    ]
    for nombre, descripcion in defaults:
        TipoLicencia.objects.get_or_create(
            nombre=nombre,
            defaults={
                "descripcion": descripcion,
                "requiere_aprobacion": True,
                "activo": True,
            },
        )


def unseed_tipos_licencia(apps, schema_editor):
    TipoLicencia = apps.get_model("recursos_humanos", "TipoLicencia")
    TipoLicencia.objects.filter(
        nombre__in=[
            "Vacaciones",
            "Licencia medica",
            "Maternidad",
            "Paternidad",
            "Permiso especial",
            "Suspension",
        ]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("recursos_humanos", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_tipos_licencia, unseed_tipos_licencia),
    ]
