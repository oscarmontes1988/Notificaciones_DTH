# notificaciones/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # La página principal (carga)
    path('', views.vista_carga, name='vista_carga'),

    # La página de resultados
    path('consolidados/', views.vista_consolidados, name='vista_consolidados'),
]