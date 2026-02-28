from django.urls import path
from . import views

urlpatterns = [
    path('empleados/', views.lista_empleados, name='lista_empleados'),
    path('licencias/', views.lista_licencias, name='lista_licencias'),
    path('vacaciones/', views.lista_vacaciones, name='lista_vacaciones'),
    path('capacitaciones/', views.lista_capacitaciones, name='lista_capacitaciones'),
]