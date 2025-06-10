from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from .forms import login_form, reg_form
from .logger import logger
import os
import json

class get_auth(APIView):
    def get(self, request):
        try:
            if request.user.is_authenticated:
                return Response({"auth":True})
            return Response({"auth":False})
        except Exception as e:
            logger.error(f"error in get_auth: {e}")
            return Response({"auth":False})

class set_login(APIView):
    def post(self, request):
        try:
            form = login_form(request.data)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                user = authenticate(request, username=username, password=password)
                if user != None:
                    login(request, user)
                    return Response({"login":True})
            return Response({"login":False})
        except Exception as e:
            logger.error(f"error in set_login: {e}")
            return Response({"login":False})

class set_reg(APIView):
    def post(self, request):
        try:
            form = reg_form(request.data)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                email = form.cleaned_data["email"]
                if User.objects.filter(username=username).exists():
                    return Response({"reg":"EXISTS"})
                else:
                    user = User.objects.create_user(username=username, password=password, email=email)
                    user.save()
                    login(request, user)
                    return Response({"reg":True})
            return Response({"reg":False})
        except Exception as e:
            logger.error(f"error in set_reg: {e}")
            return Response({"reg":False})

class set_logout(APIView):
    def post(self, request):
        try:
            logout(request)
            return Response({"logout":True})
        except Exception as e:
            logger.error(f"error in set_logout: {e}")
            return Response({"logout":False})

class get_products(APIView):
    def get(self, request):
        try:
            json_path = os.path.join(settings.BASE_DIR, 'auth_app', 'static', 'json', 'products.json')
            with open(json_path, 'r') as file:
                data = json.load(file)

            n = int(request.data.get('n'))

            data = data[n*6:(n+1)*6]

            return Response({"products":data})
        
        except Exception as e:
            logger.error(f"error in get_products: {e}")
            return Response({"products":False})