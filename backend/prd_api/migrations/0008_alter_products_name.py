# Generated by Django 5.2.2 on 2025-06-25 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prd_api', '0007_products_likes_productlikes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
