from django.db import models
from django.contrib.auth.models import User
from .Choise_Data import *

class products(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False)
    discription = models.TextField(max_length=3000, null=False)
    price = models.IntegerField(null=False)
    currency_type = models.CharField(max_length=20, choices=CURRENCY_CHOICES, null=False)
    image = models.ImageField(upload_to="files/images/", null=True)
    stars = models.IntegerField(null=True, default=0)
    likes = models.IntegerField(null=True, default=0)
    condition = models.CharField(max_length=25, null=False, default="New")
    category = models.CharField(max_length=25, null=False, default="Others", choices=CATEGORIES_CHOICES)

class ProductStars(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'user')

class ProductInCart(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'user')

class ProductLikes(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product', 'user')

class ProductComment(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=3000, null=False)

    class Meta:
        unique_together = ('product', 'user')