from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, Permission, User


MODULE_PERMISSION_GROUPS = [
    {
        "key": "auth_permissions_module",
        "title": "Autenticacion y autorizacion",
        "description": "Permisos para usuarios, grupos y seguridad del panel.",
        "app_labels": ("auth",),
    },
    {
        "key": "inventario_permissions_module",
        "title": "Inventario",
        "description": "Control de productos, movimientos y combustible.",
        "app_labels": ("inventario",),
    },
    {
        "key": "choferes_permissions_module",
        "title": "Choferes",
        "description": "Expedientes de choferes subcontratistas y conduces.",
        "app_labels": ("choferes",),
    },
    {
        "key": "pagos_permissions_module",
        "title": "Pagos",
        "description": "Registro de pagos y soporte de liquidaciones.",
        "app_labels": ("pagos",),
    },
    {
        "key": "cuentas_permissions_module",
        "title": "Cuentas",
        "description": "Cuentas por pagar, por cobrar y abonos.",
        "app_labels": ("cuentas",),
    },
    {
        "key": "rrhh_permissions_module",
        "title": "Recursos humanos",
        "description": "Gestion de empleados, licencias, vacaciones y capacitaciones.",
        "app_labels": ("recursos_humanos",),
    },
    {
        "key": "tracking_permissions_module",
        "title": "Tracking",
        "description": "Vehiculos, contenedores y disponibilidad operativa.",
        "app_labels": ("tracking",),
    },
    {
        "key": "reportes_permissions_module",
        "title": "Reportes",
        "description": "Consulta y exportacion de reportes operativos.",
        "app_labels": ("reportes",),
    },
]

MANAGED_PERMISSION_APP_LABELS = {
    app_label
    for group in MODULE_PERMISSION_GROUPS
    for app_label in group["app_labels"]
}


class ModulePermissionChoiceField(forms.ModelMultipleChoiceField):
    ACTION_LABELS = {
        "view": "Ver",
        "add": "Agregar",
        "change": "Cambiar",
        "delete": "Eliminar",
    }

    def label_from_instance(self, obj):
        codename = obj.codename
        action, _, _ = codename.partition("_")
        action_label = self.ACTION_LABELS.get(action, obj.name)
        model_class = obj.content_type.model_class()
        if model_class is not None:
            model_label = model_class._meta.verbose_name
        else:
            model_label = obj.content_type.name
        return f"{action_label} {model_label}"


class ModulePermissionFormMixin:
    module_permission_groups = MODULE_PERMISSION_GROUPS
    managed_permission_app_labels = MANAGED_PERMISSION_APP_LABELS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._module_permission_field_names = []

        for group in self.module_permission_groups:
            field_name = group["key"]
            initial = Permission.objects.none()
            if self.instance.pk:
                initial = self.instance.user_permissions.filter(
                    content_type__app_label__in=group["app_labels"],
                )
            self.fields[field_name].initial = initial
            self._module_permission_field_names.append(field_name)

    def _selected_managed_permission_ids(self):
        permission_ids = []
        for field_name in self._module_permission_field_names:
            permission_ids.extend(
                self.cleaned_data.get(field_name, Permission.objects.none()).values_list("id", flat=True)
            )
        return permission_ids

    def _preserved_unmanaged_permission_ids(self):
        if not self.instance.pk:
            return []
        return list(
            self.instance.user_permissions.exclude(
                content_type__app_label__in=self.managed_permission_app_labels,
            ).values_list("id", flat=True)
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        permission_ids = self._preserved_unmanaged_permission_ids() + self._selected_managed_permission_ids()
        self._pending_permission_ids = permission_ids

        if commit and user.pk:
            user.user_permissions.set(permission_ids)
        else:
            original_save_m2m = getattr(self, "save_m2m", None)

            def save_m2m():
                if callable(original_save_m2m):
                    original_save_m2m()
                if user.pk:
                    user.user_permissions.set(self._pending_permission_ids)

            self.save_m2m = save_m2m

        return user


class PanelUserChangeForm(ModulePermissionFormMixin, UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class PanelUserCreationForm(ModulePermissionFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff", "is_superuser")


def build_module_permission_field(group):
    queryset = Permission.objects.filter(
        content_type__app_label__in=group["app_labels"],
    ).select_related("content_type").order_by("content_type__app_label", "content_type__model", "codename")
    return ModulePermissionChoiceField(
        queryset=queryset,
        required=False,
        label=group["title"],
        help_text=group["description"],
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "module-permission-list"}
        ),
    )


def install_module_permission_fields(form_class):
    for group in MODULE_PERMISSION_GROUPS:
        field_name = group["key"]
        field = build_module_permission_field(group)
        form_class.declared_fields[field_name] = field
        form_class.base_fields[field_name] = field


install_module_permission_fields(PanelUserChangeForm)
install_module_permission_fields(PanelUserCreationForm)


class PanelUserAdmin(UserAdmin):
    add_form_template = None
    add_form = PanelUserCreationForm
    form = PanelUserChangeForm
    list_display = ("username", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self._build_add_fieldsets()

        fieldsets = [
            (None, {"fields": ("username", "password")}),
            ("Informacion personal", {"fields": ("first_name", "last_name", "email")}),
            (
                "Acceso general",
                {
                    "fields": ("is_active", "is_staff", "is_superuser"),
                    "description": "Define el nivel general de acceso al panel.",
                },
            ),
        ]

        for group in MODULE_PERMISSION_GROUPS:
            fieldsets.append(
                (
                    group["title"],
                    {
                        "fields": (group["key"],),
                        "description": group["description"],
                        "classes": ("module-permission-fieldset",),
                    },
                )
            )

        fieldsets.append(
            ("Auditoria", {"fields": ("last_login", "date_joined")}),
        )
        return fieldsets

    def _build_add_fieldsets(self):
        fieldsets = [
            (
                None,
                {
                    "classes": ("wide",),
                    "fields": (
                        "username",
                        "first_name",
                        "last_name",
                        "email",
                        "password1",
                        "password2",
                    ),
                },
            ),
            (
                "Acceso general",
                {
                    "classes": ("wide",),
                    "fields": ("is_active", "is_staff", "is_superuser"),
                    "description": "Crea el usuario y define el acceso base al panel.",
                },
            ),
        ]

        for group in MODULE_PERMISSION_GROUPS:
            fieldsets.append(
                (
                    group["title"],
                    {
                        "classes": ("wide", "module-permission-fieldset"),
                        "fields": (group["key"],),
                        "description": group["description"],
                    },
                )
            )
        return fieldsets

admin.site.unregister(User)
admin.site.register(User, PanelUserAdmin)

admin.site.unregister(Group)
