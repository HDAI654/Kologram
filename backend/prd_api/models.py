from django.db import models
from django.contrib.auth.models import User

class products(models.Model):
    currency_choices = [
        ('USD', 'US Dollar'),
        ('IRR', 'Iranian Rial'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CHF', 'Swiss Franc'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),    
        ('NZD', 'New Zealand Dollar'),
        ('CNY', 'Chinese Yuan'),
        ('INR', 'Indian Rupee'),
        ('RUB', 'Russian Ruble'),
        ('BRL', 'Brazilian Real'),
        ('ZAR', 'South African Rand'),
        ('KRW', 'South Korean Won'),
        ('MXN', 'Mexican Peso'),
        ('SGD', 'Singapore Dollar'),
        ('HKD', 'Hong Kong Dollar'),
        ('SEK', 'Swedish Krona'),
        ('NOK', 'Norwegian Krone'),
        ('TRY', 'Turkish Lira'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, null=False)
    discription = models.TextField(max_length=3000, null=False)
    price = models.IntegerField(null=False)
    currency_type = models.CharField(max_length=20, choices=currency_choices, null=False)
    image = models.ImageField(upload_to="files/images/", null=True)
    stars = models.IntegerField(null=True, default=0)
    likes = models.IntegerField(null=True, default=0)

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