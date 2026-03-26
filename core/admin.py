from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, User


class PanelUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label="Nombres", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "password1", "password2")
        labels = {"username": "Nombre de usuario"}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user


class PanelUserChangeForm(UserChangeForm):
    first_name = forms.CharField(label="Nombres", max_length=150, required=True)
    last_name = forms.CharField(label="Apellidos", max_length=150, required=True)

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"
        labels = {"username": "Nombre de usuario"}


class PanelUserAdmin(UserAdmin):
    add_form_template = None
    add_form = PanelUserCreationForm
    form = PanelUserChangeForm
    list_display = ("username", "first_name", "last_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("username", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Informacion personal", {"fields": ("first_name", "last_name")}),
        (
            "Estado",
            {
                "fields": ("is_active",),
                "description": "Todos los usuarios tienen acceso completo al sistema.",
            },
        ),
        ("Auditoria", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "first_name", "last_name", "password1", "password2"),
                "description": "Completa los datos basicos para crear el usuario con acceso total al sistema.",
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.is_staff = True
        obj.is_superuser = True
        obj.is_active = True
        super().save_model(request, obj, form, change)


admin.site.unregister(User)
admin.site.register(User, PanelUserAdmin)

admin.site.unregister(Group)
