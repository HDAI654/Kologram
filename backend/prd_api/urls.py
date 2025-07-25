from django.urls import path
from .views import *

urlpatterns = [
    path('get_products/', get_products.as_view(), name='get_products'),
    path('search-prd/', search_products.as_view()),
    path('is-starred/', HasUserStarredProduct.as_view()),
    path('chn-star/', ChangeStar.as_view()),
    path('is-inCart/', isProductInCart.as_view()),
    path('chn-inCart/', ChangeInCart.as_view()),
    path('addPrd/', AddPrd.as_view()),
    path('delPrd/', DelPrd.as_view()),
    path('editPrd/', EditProductView.as_view()),
    path('get-comments/', GetPrdComment.as_view()),
    path('add-comment/', AddProductComment.as_view()),
    path('getChoiseData/', getChoiseData.as_view()),
    path('getCategories/', getCategories.as_view()),
    path('all-prd-ids/', AllProductIDs.as_view()),
    path('getPrdByID/', getPrdByID.as_view()),
    path('get-top-prds/', GetTopPrds.as_view()),
]