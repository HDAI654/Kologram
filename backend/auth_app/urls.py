from django.urls import path
from .views import *

urlpatterns = [
    path('get_auth/', get_auth.as_view(), name='get_auth'),
    path('login/', set_login.as_view(), name='login'),
    path('reg/', set_reg.as_view(), name='reg'),
    path('logout/', set_logout.as_view(), name='logout'),
    path('get_products/', get_products.as_view(), name='get_products'),
]