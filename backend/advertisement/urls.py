from django.urls import path
from .views import *

urlpatterns = [
    path('get-banners/', getBanners.as_view()),
    path('get-offers/', getOffers.as_view()),
]