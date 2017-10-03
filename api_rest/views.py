from django.shortcuts import render
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from models import *

from django.views.decorators.csrf import csrf_exempt

import json

# Create your views here.

#pedir el token para conversar entre app y servidor
def handshaking(request):
	response_data = {
		"csrf_token": get_token(request)
	}

	return HttpResponse(json.dumps(response_data), content_type = "application/json")

#verificar el login
@csrf_exempt 
def login(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		user_name = received_data['correo']
		passw = received_data['pass']
		user = authenticate(username=user_name, password = passw)
		if user is not None:
			return HttpResponse(json.dumps({'logged': True}), content_type = "application/json")
		else:
			return HttpResponse(json.dumps({'logged': False}), content_type = "application/json")

#almacenar usuario
@csrf_exempt 
def almacenarUsuario(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		nombre = received_data['nombre']
		correo = received_data['correo']
		password = received_data['pass']		
		try: 
			usuario = Usuario.objects.get(username = correo)
			response_data = { 				
					"mensaje": "Este usuario ya existe.",
					"almacenado": False
				} 		
		except ObjectDoesNotExist:
#To DO: mandarle un mail con sus datos
			usuario = Usuario(first_name=nombre, username=correo, password=password)
			usuario.save()
			response_data = { 				
					"mensaje": "Cuenta creada existosamente.",
					"almacenado": True
				} 
		return HttpResponse(json.dumps(response_data), content_type = "application/json")


#buscar las entradas que posee cierto usuario para una determinada empresa 
@login_required   #pistola
def usarEntrada(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		usuario_id = received_data['id_usuario']
		empresa_id = received_data['id_empresa']
		discount = False
		try:
			#repetir hasta encontrar una entrada valida
			while not discount:
				#obtener LA entrada mas cercana a vencer				
				entrada = Tinket.objects.filter(usuario=usuario_id, empresa=empresa_id, valido=True).order_by('fecha_expiracion')[0]
				if not entrada:
					return_data = { 
						"discount": False, 
						#"id_tinket": entrada.id
						"mensaje": "No posees entradas disponibles."
					}
					return HttpResponse(json.dumps(return_data), content_type = "application/json")

				send_data = { 
					"id_entrada": entrada.id_ticket 
				}
				empresa = Empresa.objects.get(pk=empresa_id)
				url = empresa.ip+empresa.puerto+'/'+empresa.nombre+'/discount'

				#Hacemos la consulta al servidor de la empresa
				response = request.post(url, send_data)
				response_data = json.loads(response.text('utf-8')) 

				discount = response_data['discount']
				Tinket.objects.filter(id=entrada.id).update(valido=False)

				if discount == True:
					return_data = { 
						"discount": True, 
						#"id_tinket": entrada.id
						"mensaje": "Entrada utilizada exitosamente."
					}
				else:
					return_data = { 
						"discount": False, 
						#"id_tinket": entrada.id
						"mensaje": "No posees entradas disponibles."
					}
		except ObjectDoesNotExist:
			return_data = { 
					"discount": False, 
					#"id_tinket": entrada.id					
					"mensaje": "No posees entradas disponibles."
				} 
		return HttpResponse(json.dumps(return_data), content_type = "application/json")

#valida una entrada, la marca como valida, le tiene que avisar a la empresa que la use
#la empresa me devuelve el id tinket y discount
#falta consultarle a la empresa
#@login_required
#def validarEntrada(request):
#	if request.method == 'POST':
#		received_data = json.loads(request.body.decode('utf-8'))
#		id_tinket = received_data['id_tinket']
#		discount = received_data['discount']
#		if discount == True:
#			Tinket.objects.filter(id=id_tinket).update(valido=False)



@login_required        #app
def entradasDisponibles(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		usuario_id = received_data['usuario_id']
		entradas = Tinket.objects.filter(usuario=usuario_id, valido=True)
		if not entradas:
			response_data = { 				
				"mensaje": "No hay entradas disponibles.",
				"entradas": False					
			}
		else:
			response_data = []
			for entrada in entradas:
				response_data.append({
					"id": entrada.id,
					"fecha_emision": entrada.fecha_emision.isoformat(),
					"fecha_utilizacion": entrada.fecha_utilizacion.isoformat(),
					"fecha_expiracion": entrada.fecha_expiracion.isoformat(),
					"valido": entrada.valido
				})

		return HttpResponse(json.dumps(response_data), content_type = "application/json")
	
		#parseo del query object para enviar en un json

@login_required			#app
def entradasUtilizadas(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		usuario_id = received_data['usuario_id']
		entradas = Tinket.objects.filter(usuario=usuario_id, valido=False)
		if not entradas:
			response_data = { 				
				"mensaje": "No has utilizado ninguna entrada.",
				"entradas": False					
			} 
		return HttpResponse(json.dumps(response_data), content_type = "application/json")
	
		#parseo del query object para enviar en un json


#obtener info ticket id ticket y nombre empresa 
@login_required 	#app 
def detalleEntrada(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		id_tinket = received_data['id_tinket']
		empresa_nombre = received_data['empresa_nombre']
		try:
			entrada = Tinket.objects.get(pk=id_tinket)
			
			send_data = { 
				"id_ticket": entrada.id_ticket 
			}
			empresa = Empresa.objects.get(nombre=empresa_nombre)
			url = empresa.ip+empresa.puerto+'/'+empresa.nombre+'/check'

			response = request.post(url, send_data)
			response_data = json.loads(response.text('utf-8')) #lo que me devuelve el oscar

			tinket = Tinket(fecha_emision=response_data.fecha_emision,fecha_utilizacion=None,fecha_expiracion=response_data.fecha_expiracion,valido=response_data.valido,id_ticket=id_ticket,usuario=usuario,empresa=empresa.id)
			tinket.save()
			
		except ObjectDoesNotExist:
			response_data = { 
				"mensaje": "Detalle entrada no disponible",
				"detalle": False
#To DO: que el oscar nos devuelva detalle = true
			}
		return HttpResponse(json.dumps(response_data), content_type = "application/json") #envio a la app



#almacenar tinket en base a: id registro fecha fecha_expiracionestado costo detalle empresa
@login_required    #app
def almacenarTinket(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		id_ticket = received_data['id_ticket']
		empresa_nombre = received_data['empresa']
		usuario = received_data['usuario']
		send_data = { 
				"id_ticket": id_ticket 
			}
		try:
			empresa = Empresa.objects.get(nombre=empresa_nombre)
			url = empresa.ip+empresa.puerto+'/'+empresa.nombre+'/check'

			response = request.post(url, send_data)
			response_data = json.loads(response.text('utf-8'))
#TO DO: none funciona para fecha?
			tinket = Tinket(fecha_emision=response_data.fecha_emision,fecha_utilizacion=None,fecha_expiracion=response_data.fecha_expiracion,valido=response_data.valido,id_ticket=id_ticket,usuario=usuario,empresa=empresa.id)
			tinket.save()

			response_data = { 
				"mensaje": "Tinket almacenado exitosamente.",
				"almacenar": True
			}
		except ObjectDoesNotExist:
			response_data = { 
				"mensaje": "La empresa no existe",
				"almacenar": False
			}





