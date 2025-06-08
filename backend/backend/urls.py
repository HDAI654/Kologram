from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin_page/', admin.site.urls),
    path('auth/', include("auth_app.urls")),
]
