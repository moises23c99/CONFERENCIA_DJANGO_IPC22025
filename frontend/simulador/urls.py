from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cargar_config/', views.cargar_configuracion, name='cargar_configuracion'),
    path('cargar_consumo/', views.cargar_consumo, name='cargar_consumo'),
    path('consultar_datos/', views.consultar_datos, name='consultar_datos'),
    path('crear_recurso/', views.crear_datos, name='crear_datos'),
]
