from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import login_form, reg_form
from logger import logger

class get_auth(APIView):
    def get(self, request):
        try:
            if request.user.is_authenticated:
                return Response({"auth":True})
            return Response({"auth":False})
        except Exception as e:
            logger.error(f"error in get_auth: {e}")
            return Response({"auth":"ERROR"}, status=500)

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
                    return Response({"login":True}, status=200)
                return Response({"login":False}, status=401)
            return Response({"login":False}, status=422)
        except Exception as e:
            logger.error(f"error in set_login: {e}")
            return Response({"login":False}, status=500)

class set_reg(APIView):
    def post(self, request):
        try:
            form = reg_form(request.data)
            if form.is_valid():
                username = form.cleaned_data["username"]
                password = form.cleaned_data["password"]
                email = form.cleaned_data["email"]
                if User.objects.filter(username=username).exists():
                    return Response({"reg":"EXISTS"}, status=409)
                else:
                    user = User.objects.create_user(username=username, password=password, email=email)
                    user.save()
                    login(request, user)
                    return Response({"reg":True})
            return Response({"reg":False}, status=422)
        except Exception as e:
            logger.error(f"error in set_reg: {e}")
            return Response({"reg":False}, status=500)

class set_logout(APIView):
    def post(self, request):
        try:
            if request.user.is_authenticated:
                logout(request)
                return Response({"logout":True})
            return Response({"logout":"NO_LOGIN", "msg": "You are not logged in, so you cannot log out."}, status=401)
        except Exception as e:
            logger.error(f"error in set_logout: {e}")
            return Response({"logout":False}, status=500)