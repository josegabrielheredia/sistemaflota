from django.urls import path
from . import views

urlpatterns = [
    path('empleados/', views.lista_empleados, name='lista_empleados'),
    path('pagos/', views.lista_pagos_empleados, name='lista_pagos_empleados'),
    path('gastos/', views.lista_gastos_rrhh, name='lista_gastos_rrhh'),
    path('licencias/', views.lista_licencias, name='lista_licencias'),
    path('vacaciones/', views.lista_vacaciones, name='lista_vacaciones'),
    path('capacitaciones/', views.lista_capacitaciones, name='lista_capacitaciones'),
]
