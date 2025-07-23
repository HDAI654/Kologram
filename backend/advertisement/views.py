from logger import logger
from .models import Banners, Offer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.http import JsonResponse

class getBanners(APIView):
    def get(self, request):
        try:
            banners = Banners.objects.all()
            banners_list = [{
                "image": banner.image.url,
                "link": banner.link,
                "text": banner.text,
                "title": banner.title
            } for banner in banners]
            print(banners_list)
            if banners_list == []:
                return Response({"banners": [], "error":"no banners found"}, status=404)
            return Response({"banners": banners_list, "error": False}, status=200)
        except Exception as e:
            logger.error(f"error in getBanners: {e}")
            return Response({"banners": False, "error":"error in getting banners"}, status=500)


class getOffers(APIView):
    def get(self, request):
        offers = Offer.objects.filter(end_time__gt=now()).order_by('end_time').values(
            'title', 'description', 'link', 'end_time'
        )
        return JsonResponse(list(offers), safe=False)