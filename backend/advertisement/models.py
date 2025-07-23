from django.db import models

class Banners(models.Model):
    image = models.ImageField(upload_to='files/banners/')
    link = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    text = models.CharField(max_length=100, blank=True, null=True)

class Offer(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.CharField(max_length=100, blank=True, null=True)
    end_time = models.DateTimeField()