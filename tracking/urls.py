from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_vehiculos, name='lista_vehiculos'),
]