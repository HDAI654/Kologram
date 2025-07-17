from logger import logger
from .models import Banners
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.models import User

class getBanners(APIView):
    def get(self, request):
        try:
            banners = Banners.objects.all()
            banners_list = [{
                "image": banner.image.url
            } for banner in banners]
            print(banners_list)
            if banners_list == []:
                return Response({"banners": [], "error":"no banners found"}, status=404)
            return Response({"banners": banners_list, "error": False}, status=200)
        except Exception as e:
            logger.error(f"error in getBanners: {e}")
            return Response({"banners": False, "error":"error in getting banners"}, status=500)
