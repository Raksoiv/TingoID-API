from django.conf.urls import url
from . import views

##url de la api
urlpatterns = [
	url(r'handshaking/', views.handshaking),
	url(r'login/', views.login),
	url(r'usarEntrada/', views.usarEntrada),
	url(r'almacenarUsuario/',views.almacenarUsuario),
	url(r'entradasDisponibles/',views.entradasDisponibles),
	url(r'entradasUtilizadas/',views.entradasUtilizadas),
	url(r'detalleEntrada/',views.detalleEntrada),
	url(r'almacenarTinket/',views.almacenarTinket)
]