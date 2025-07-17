from django.db import models

class Banners(models.Model):
    image = models.ImageField(upload_to='files/banners/')
