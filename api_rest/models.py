from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuario(AbstractUser):
	pass
	


class Empresa (models.Model):
	nombre = models.CharField(max_length=200)
	ip = models.CharField(max_length=16)
	puerto = models.CharField(max_length=6)

	usuario = models.ForeignKey('Usuario')

class Dispositivo(models.Model):
	android_id = models.CharField(max_length=18)

	usuario=models.ForeignKey('Usuario')


class Tinket(models.Model):
	fecha_emision = models.DateField()
	fecha_expiracion = models.DateField()
	fecha_utilizacion = models.DateField(null=True)
	valido = models.BooleanField()
	id_ticket = models.CharField(max_length=100)

	usuario = models.ForeignKey('Usuario')
	empresa = models.ForeignKey('Empresa')
