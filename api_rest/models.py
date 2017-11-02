from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Usuario(AbstractUser):
	pass
	tiempo_qr = models.DateTimeField(null=True)
	imagen = models.ImageField(blank=True, null=True)

class Empresa (models.Model):
	nombre = models.CharField(max_length=200)
	ip = models.CharField(max_length=16)
	puerto = models.CharField(max_length=6)

	usuario = models.ForeignKey('Usuario')

class Tinket(models.Model):
	fecha_emision = models.DateField()
	fecha_expiracion = models.DateField()
	fecha_utilizacion = models.DateField(null=True)
	valido = models.BooleanField()
	id_ticket = models.CharField(max_length=100)
	tipo = models.CharField(max_length=100)

	usuario = models.ForeignKey('Usuario')
	empresa = models.ForeignKey('Empresa')

class Promocion(models.Model):
	promocion_id = models.CharField(max_length=100)
	fecha_emision = models.DateField()
	fecha_expiracion = models.DateField()
	meta = models.CharField(max_length=100)
	imagen = models.ImageField(blank=True, null=True)
	descripcion = models.CharField(max_length=500)
	disponible = models.BooleanField()

	empresa = models.ForeignKey('Empresa')

class Avance(models.Model):
	valido = models.BooleanField()
	avance = models.CharField(max_length=100)
	codigo = models.CharField(max_length=100, null=True)

	usuario = models.ForeignKey('Usuario')
	promocion = models.ForeignKey('Promocion')
