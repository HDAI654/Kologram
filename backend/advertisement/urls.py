from django.urls import path
from .views import *

urlpatterns = [
    path('get-banners/', getBanners.as_view(), name='get_products'),
]