from django.db import models
from django.contrib.auth.models import User
from .Choise_Data import *

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=3000)
    price = models.IntegerField()
    currency_type = models.CharField(max_length=20, choices=CURRENCY_CHOICES)
    image = models.ImageField(upload_to="files/images/", null=True, blank=True)
    stars = models.IntegerField(default=0, null=True)
    category = models.CharField(max_length=25, default="others", choices=CATEGORIES_CHOICES)

    digital_file = models.FileField(upload_to='files/digital/')
    file_format = models.CharField(max_length=10, blank=True, null=True)
    file_size = models.IntegerField(blank=True, null=True)
    download_count = models.IntegerField(default=0)
    tags = models.CharField(max_length=200, blank=True)
    license_type = models.CharField(max_length=50, blank=True, null=True)
    is_free = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductStars(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'user')

class ProductInCart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'user')

class ProductComment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=3000, null=False)

    class Meta:
        unique_together = ('product', 'user')