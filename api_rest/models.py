from django.db import models

# Create your models here.

class Usuario(models.Model):
	nombre = models.CharField(max_length = 200)
	correo = models.EmailField()
	password = models.CharField(max_length=200)


class Empresa (models.Model):
	nombre = models.CharField(max_length=200)
	ip = models.CharField(max_length=16)
	puerto = models.CharField(max_length=6)


class Dispositivo(models.Model):
	mac = models.CharField(max_length=18)

	usuario=models.ForeignKey('Usuario')


class Tinket(models.Model):
	fecha_emision = models.DateField()
	fecha_expiracion = models.DateField()
	valido = models.BooleanField()

	usuario = models.ForeignKey('Usuario')
	empresa = models.ForeignKey('Empresa')
