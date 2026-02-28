from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_cuentas, name='lista_cuentas'),
]