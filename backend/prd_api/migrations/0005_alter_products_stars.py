# Generated by Django 5.2.2 on 2025-06-16 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prd_api', '0004_alter_products_discription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='stars',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
