from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_choferes, name='lista_choferes'),
    path('registrar/', views.registrar_chofer, name='registrar_chofer'),
]
