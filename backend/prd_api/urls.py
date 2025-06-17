from django.urls import path
from .views import *

urlpatterns = [
    path('get_products/', get_products.as_view(), name='get_products'),
    path('is-starred/', HasUserStarredProduct.as_view()),
    path('chn-star/', ChangeStar.as_view()),
    path('is-inCart/', isProductInCart.as_view()),
    path('chn-inCart/', ChangeInCart.as_view()),
]