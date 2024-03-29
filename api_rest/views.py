from django.shortcuts import render
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from .models import *
import requests
import base64
from django.utils import timezone
from datetime import timedelta 
from datetime import date
import time

from django.views.decorators.csrf import csrf_exempt

import json

# Create your views here.

#pedir el token para conversar entre app y servidor
def handshaking(request):
	response_data = {
		"csrf_token": get_token(request)
	}

	return HttpResponse(json.dumps(response_data), content_type = "application/json")


################# USUARIO #########################

#verificar el login
@csrf_exempt 
def login(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		user_name = str(received_data['correo'])
		passw = str(received_data['pass'])
		try: 
			user = Usuario.objects.get(username=user_name, password=passw)
			response_data = { 	
				"id": user.id,
				"logged":True
				}
			return HttpResponse(json.dumps(response_data), content_type = "application/json")
		except ObjectDoesNotExist:
			response_data = { 	
				"logged":False
				}
			return HttpResponse(json.dumps(response_data), content_type = "application/json")

#almacenar usuario
@csrf_exempt 
def almacenarUsuario(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		nombre = received_data['nombre']
		apellido = received_data['apellido']
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
			usuario = Usuario(
				first_name=nombre, 
				last_name=apellido, 
				username=correo, 
				password=password,
				email=correo)
			usuario.save()
			response_data = { 				
					"mensaje": "Cuenta creada existosamente.",
					"almacenado": True
				} 
		return HttpResponse(json.dumps(response_data), content_type = "application/json")

############################## ENTRADAS ############################################

#@login_required        #app
@csrf_exempt   #si la fecha e expiracion es menor a la fecha actual
def entradasDisponibles(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		correo = received_data['correo']
		try:
			usuario = Usuario.objects.get(username=correo)
			entradas = Tinket.objects.filter(usuario=usuario.id,valido=True)
			if not entradas:
				response_data = []
			else:
				response_data = []
				for entrada in entradas:
					response_data.append({
						"id": entrada.id,
						"fecha_emision": entrada.fecha_emision.isoformat(),
						"fecha_utilizacion": entrada.fecha_utilizacion.isoformat(),
						"fecha_expiracion": entrada.fecha_expiracion.isoformat(),#
						"valido": entrada.valido,
						"empresa": entrada.empresa.nombre#
					})
		except ObjectDoesNotExist:
			response_data = []

		return HttpResponse(json.dumps(response_data), content_type = "application/json")
		

@csrf_exempt		#app
def entradasUtilizadas(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		correo = received_data['correo']
		try:
			usuario = Usuario.objects.get(username=correo)
			entradas = Tinket.objects.filter(usuario=usuario.id,valido=False)
			if not entradas:
				response_data = []
			else:
				response_data = []
				for entrada in entradas:

					response_data.append({
						"id": entrada.id,
						"fecha_emision": entrada.fecha_emision.isoformat(),
						"fecha_utilizacion": entrada.fecha_utilizacion.isoformat(),
						"fecha_expiracion": entrada.fecha_expiracion.isoformat(),
						"valido": entrada.valido,
						"empresa": entrada.empresa.nombre
					})
		except ObjectDoesNotExist:
			response_data = []

		return HttpResponse(json.dumps(response_data), content_type = "application/json")

#obtener info ticket id ticket y nombre empresa 
@csrf_exempt	#app 
def detalleEntrada(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		id_tinket = received_data['id_tinket']
		#empresa_nombre = received_data['empresa_nombre']

		try:
			tinket_previo= Tinket.objects.get(id=id_tinket)
			print("uno")
			empresa_nombre= tinket_previo.empresa.nombre
			if not tinket_previo:
				response_data = { 
					"mensaje": "Detalle entrada no disponible.",
					"detalle": False
					}

			send_data = { 
				"id_ticket": tinket_previo.id_ticket 
			}

			empresa = Empresa.objects.get(nombre=empresa_nombre)
			url = 'http://'+empresa.ip+empresa.puerto+'/'+empresa.nombre+'/detalle'

			response = requests.post(url, json.dumps(send_data))
			response_data = json.loads(response.text)		

			#si existe, verifico si el estado continua siendo el mismo			
			
			if str(response_data['encontrado'])=='True':

				tinket_previo.valido=str(response_data['valido'])
				tinket_previo.save()

				response_data = {
					"id": tinket_previo.id,
					"fecha_emision": tinket_previo.fecha_emision.isoformat(),
					"fecha_utilizacion": tinket_previo.fecha_utilizacion.isoformat(),
					"fecha_expiracion": tinket_previo.fecha_expiracion.isoformat(),
					"valido": tinket_previo.valido,
					"empresa": tinket_previo.empresa.nombre,
					"tipo":str(response_data['tipo']),
					"valor":str(response_data['valor']),
					"detalle":True

					}
			else:
				response_data = { 
				"mensaje": "Ticket no encontrado en la empresa.",
				"detalle": False
				}

			
		except ObjectDoesNotExist:
			response_data = { 
				"mensaje": "Detalle entrada no disponible.",
				"detalle": False
				}
		return HttpResponse(json.dumps(response_data), content_type = "application/json") #envio a la app



#almacenar tinket en base a: id registro fecha fecha_expiracionestado costo detalle empresa
#@login_required    #app
@csrf_exempt 
def almacenarTinket(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		id_ticket = received_data['id_tinket']
		empresa_nombre = received_data['empresa']
		usuario = Usuario.objects.filter(username=str(received_data['usuario'])).get()
		send_data = { 
				"id_ticket": id_ticket 
			}
		try:
			print(empresa_nombre)
			aqui='uno'
			empresa = Empresa.objects.get(nombre=empresa_nombre)
			url = 'http://'+empresa.ip+empresa.puerto+'/'+empresa.nombre+'/detalle'

			response = requests.post(url, json.dumps(send_data))
			response_data = json.loads(response.text)

			if str(response_data['encontrado'])=='True':

				tinket = Tinket(
					fecha_emision=str(response_data['fecha_emision']),
					fecha_utilizacion='2050-12-12',
					fecha_expiracion=str(response_data['fecha_expiracion']),
					valido=str(response_data['valido']),
					id_ticket=id_ticket,
					usuario=usuario,
					empresa=empresa)

				#si existe no  lo almacena
				aqui='dos'
				tinket_previo= Tinket.objects.get(id_ticket=id_ticket, empresa=empresa)
				
				response_data = { 
					"mensaje": "Tinket ya existente.",
					"almacenar": False
				}
			else:
				response_data = { 
					"mensaje": "La empresa no posee ese ticket.",
					"almacenar": False
				}
		except ObjectDoesNotExist:
			print(aqui)

			if aqui == 'uno':
				response_data = { 
					"mensaje": "La empresa no existe",
					"almacenar": False
				}
			if aqui == 'dos':
				tinket.save()
				response_data = { 
					"mensaje": "Tinket almacenado exitosamente.",
					"almacenar": True
				}
		return HttpResponse(json.dumps(response_data), content_type = "application/json") #envio a la app


@csrf_exempt   
def usarEntrada(request):   ##logica para el casino, usar la entrada mas cercana a vencer
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		usuario_id = received_data['id_usuario']
		empresa_id = received_data['id_empresa']
		discount = False
		try: 
			usuario = Usuario.objects.filter(id=usuario_id).get()
			#ver que el QR no haya expirado
			#fe=datetime.strptime(usuario.tiempo_qr, '%Y-%m-%d')
			#print (usuario.tiempo_qr)
			#print (datetime.now())						
			if usuario.tiempo_qr > datetime.now(timezone.utc):
				try:
					#repetir hasta encontrar una entrada valida
					while not discount:
						#obtener LA entrada mas cercana a vencer				
						entrada = Tinket.objects.filter(usuario=usuario_id, empresa=empresa_id, valido=True).order_by('fecha_expiracion').first()
						if not entrada:
							return_data = { 
								"discount": False, 
								#"id_tinket": entrada.id
								"mensaje": "No posees entradas disponibles."
							}
							return HttpResponse(json.dumps(return_data), content_type = "application/json")

						send_data = { 
							"id_ticket": entrada.id_ticket 
						}

						empresa = Empresa.objects.get(id=empresa_id)
						url = 'http://'+empresa.ip+empresa.puerto+'/'+empresa.nombre+'/discount'

						#Hacemos la consulta al servidor de la empresa
						response = requests.post(url, json.dumps(send_data))
						response_data = json.loads(response.text)
						discount = str(response_data['discount'])

						if str(response_data['encontrado'])=='True':
							if discount == 'True':
								entrada.valido= False
								entrada.save()
								#suma puntos a los avances de las promociones disponibles de esa empresa
								try:
									promociones = Promocion.objects.filter(empresa=empresa,disponible=True)
									for promocion in promociones:
										avances = Avance.objects.filter(usuario=usuario,promocion=promocion)
										for avance in avances:
											avance.avance = str(int(avance.avance)+1)
											avance.save()

								except ObjectDoesNotExist:
									print("no encontro la promocion")
									continue

								return_data = { 
									"discount": True, 
									"mensaje": "Entrada utilizada exitosamente."
								}
							else:
								return_data = { 
									"discount": False, 
									"mensaje": "No posee entradas disponibles."
								}
						else:
							return_data = { 
									"discount": False, 
									"mensaje": str(response_data['error'])
								}
				except ObjectDoesNotExist:
					return_data = { 
							"discount": False, 				
							"mensaje": "No posees entradas disponibles."
						} 
			else:
				return_data = { 
							"discount": False, 				
							"mensaje": "QR mostrado ha expirado."
						} 
		except ObjectDoesNotExist:
					return_data = { 
							"discount": False, 				
							"mensaje": "No se encontro el usuario."
						} 		
		return HttpResponse(json.dumps(return_data), content_type = "application/json")




########################################### PROMOCIONES ########################
@csrf_exempt   
def promocionesExistentes(request):    #almacena en la bd de tingo las promociones de la empresa si son nuevas o las actualiza
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))				
		try:
			usuario = Usuario.objects.filter(username=str(received_data['usuario'])).get()	

			empresas = Empresa.objects.filter()
			send_data = { 
				"promociones": True 
				}
			#Consulto a todas las empresas sus promociones
			for empresa in empresas:
				url = 'http://'+empresa.ip+empresa.puerto+'/'+empresa.nombre+'/promociones'

				response = requests.post(url, json.dumps(send_data))
				response_data = json.loads(response.text)
			
				for dato in response_data:
					# me fijo que no haya pasado la fecha de vencimiento
					fe=datetime.strptime(dato['fecha_expiracion'], '%Y-%m-%d')
					disponible = fe.date() > date.today()
						
					try: #si la promocion ya esta almacenada, actualizo
						guardado = Promocion.objects.get(promocion_id=int(dato['promocion_id']), empresa = empresa)
						guardado.disponible = disponible
						guardado.save()

					except ObjectDoesNotExist: #si la promocion es nueva, la almaceno

						print('nueva')
						
						print('esta disponible')
						if dato['imagen'] == None:
							mi_imagen = ''
						else:
							mi_imagen =base64.b64encode(dato['imagen'])
						promocion = Promocion(
							promocion_id = dato['promocion_id'],
							fecha_emision = dato['fecha_emision'],
							fecha_expiracion = dato['fecha_expiracion'],
							meta = dato['meta'],
							descripcion = dato['descripcion'],
							imagen = mi_imagen,#base64.b64decode(dato['imagen']),
							disponible = disponible,
							empresa = empresa
							)
						print (promocion)
						promocion.save()
			return_data = {
				"actualizado":True
			}
			
		except ObjectDoesNotExist:		
			return_data = {
				"actualizado":False
			}	
	return HttpResponse(json.dumps(return_data), content_type = "application/json")


@csrf_exempt   
def detallePromocion(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		id_promocion = str(received_data['id_promocion'])
		id_avance = str(received_data['id_avance'])
		try:
			usuario = Usuario.objects.filter(username=str(received_data['usuario'])).get()
			promocion = Promocion.objects.filter(id=id_promocion).get()
			if promocion.imagen == None:
				mi_imagen = ''
			else:
				mi_imagen =base64.b64encode(promocion.imagen)
			#si el avance cumplido, puede mostrar boton de genrar codigo
			try:
				avance = Avance.objects.filter(id=id_avance).get()
				if avance.avance >= promocion.meta:
					generar_codigo = True

				else:
					generar_codigo = False

				return_data = { 
					"id_promocion":promocion.id,
					"id_avance":id_avance,
					"fecha_emision": promocion.fecha_emision.isoformat(),
					"fecha_expiracion": promocion.fecha_expiracion.isoformat(),
					"meta": str(promocion.meta),
					"descripcion": promocion.descripcion,
					"imagen": mi_imagen,
					"empresa": promocion.empresa.nombre,
					"encontrado":True,
					"generar_codigo":generar_codigo
					}
			except ObjectDoesNotExist:
				print("no encontro avance")
		except ObjectDoesNotExist:
			return_data = {
				"encontrado":False
			}
		return HttpResponse(json.dumps(return_data), content_type = "application/json")

@csrf_exempt   
def generarAvance(request): #me fijo que el usuario tenga una avance de TODAS las promociones de las empresas que tenga una entrada
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		#id_promocion_t = str(received_data['id'])
		try:
			usuario = Usuario.objects.filter(username=str(received_data['usuario'])).get()
			#primero tengo que ver las empresas que tiene entradas el usuario			
			tuplas_empresa = Tinket.objects.filter(usuario=usuario.id).order_by().values_list('empresa').distinct()
			for tupla in tuplas_empresa:
				#por cada empresa, ver las promociones disponibles
				try:
					empresa = Empresa.objects.filter(id=tupla[0]).get()
					promociones = Promocion.objects.filter(disponible=True, empresa=empresa)
					for promocion in promociones:
						#por cada promocion disponible, ver que tenga su avance, si no lo tiene creo la instancia
						try:
							#si la encuentra  no hace nada
							avance = Avance.objects.filter(usuario=usuario, promocion=promocion).get()
							#si no esta, tiene que crearla
						except ObjectDoesNotExist:
							#si la meta de la promocion es 1, su avance es uno, de lo contrario es cero.
							if promocion.meta == 1:
								avance_inicial = "1"
							else:
								avance_inicial = "0"

							avance = Avance(
								valido = True,
								avance = avance_inicial,
								codigo = None,
								usuario = usuario,
								promocion = promocion
							)
							avance.save()
				except ObjectDoesNotExist:
					print ("no hay promociones o no encontro la empresa")
					continue
			return_data={
				"actualizado":True
			}
		except ObjectDoesNotExist:
			print("no encontro el usuario")
			return_data={
				"actualizado":False
			}			
		return HttpResponse(json.dumps(return_data), content_type = "application/json")

@csrf_exempt   
def generarCodigo(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		id_avance = str(received_data['id_avance'])		
		try:	
			existe = Avance.objects.filter(id=id_avance).get()
			#si el avance esta completado_avance, valido=True).get()
			if (existe.promocion.disponible==True):#si la promo sigue disponible
				#la empresa me entrega codigos
				try:
					empresa = Empresa.objects.filter(id=existe.promocion.empresa.id).get()
					print(existe.promocion.promocion_id)
					print(existe.id)
					print(existe.promocion.id)
					send_data = { 
						"id_promocion": str(existe.promocion.promocion_id) 
						}
					
					url = 'http://'+empresa.ip+empresa.puerto+'/'+empresa.nombre+'/getcode'

					response = requests.post(url, json.dumps(send_data))
					response_data = json.loads(response.text)
					if str(response_data['encontrado'])=='True':
						print(True)
						return_data={
								"codigo":str(response_data['codigo_promocion']),
								"encontro":True
							}					
				except ObjectDoesNotExist:
					print("no encontro empresa")
					return_data={
							"encontro":False
						}				
		except ObjectDoesNotExist:
			print("no tiene avance")
			return_data={
					"encontro":False
				}
		return HttpResponse(json.dumps(return_data), content_type = "application/json")


@csrf_exempt   
def mostrarPromociones(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))		
		try: 
			usuario = Usuario.objects.filter(username=str(received_data['usuario'])).get()
			#promociones que se estan siguiendo y no se han utilizado
			avances = Avance.objects.filter(usuario=usuario,valido=True)
			if not avances:
				return_data = []
			else:
				return_data = []
				for avance in avances:					
					return_data.append({
							"id_avance":str(avance.id), 
							"id_promocion":str(avance.promocion.id),
							"descripcion": avance.promocion.descripcion,
							"fecha_expiracion": avance.promocion.fecha_expiracion.isoformat(),
							"empresa": avance.promocion.empresa.nombre,
							"avance": str(avance.avance),
							"meta": str(avance.promocion.meta)
						})
		except ObjectDoesNotExist:
			return_data = []
		return HttpResponse(json.dumps(return_data), content_type = "application/json")


############################### ver QR ###################################

@csrf_exempt   
def mostrarQR(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))

		try: 
			usuario = Usuario.objects.filter(username=str(received_data['usuario'])).get()
			#viejo =  datetime.now() + timedelta(days=10)  
			usuario.tiempo_qr = datetime.now(timezone.utc) + timedelta(minutes=5)
			usuario.save()
			return_data={
				"tiempo":True,
				"id": str(usuario.id),
				"tiempo max": str(usuario.tiempo_qr)
			}
	
		except ObjectDoesNotExist:
			print('no existe el usuario')			
			return_data={"tiempo":False}
	return HttpResponse(json.dumps(return_data), content_type = "application/json")

			

			
