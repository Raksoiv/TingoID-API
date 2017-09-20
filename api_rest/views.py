from django.shortcuts import render
from django.middleware.csrf import get_token
from django.http import HttpResponse
from django.contrib.auth import authenticate

import json

# Create your views here.

def handshaking(request):
	response_data = {
		"csrf_token": get_token(request)
	}

	return HttpResponse(json.dumps(response_data), content_type = "application/json")

def login(request):
	if request.method == 'POST':
		received_data = json.loads(request.body.decode('utf-8'))
		user = authenticate(username=received_data['user'], password = received_data['pass'])
		if user is not None:
			return HttpResponse(json.dumps(True), content_type = "application/json")
		else:
			return HttpResponse(json.dumps(False), content_type = "application/json")


