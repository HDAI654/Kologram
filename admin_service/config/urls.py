from django.contrib import admin
from django.urls import path

admin.site.site_header = "Kologram Admin"
admin.site.site_title = "Kologram Admin"
admin.site.index_title = "Marketplace administration"

urlpatterns = [
    path("admin/", admin.site.urls),
]
