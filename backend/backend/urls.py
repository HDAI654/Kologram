from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin_page/', admin.site.urls),
    path('auth/', include("auth_app.urls")),
    path('prd-api/', include("prd_api.urls")),
    path('ad/', include("advertisement.urls")),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
