from django.conf.urls import url
from . import views

##url de la api
urlpatterns = [
	url(r'handshaking/', views.handshaking),
	url(r'login/', views.login)
]