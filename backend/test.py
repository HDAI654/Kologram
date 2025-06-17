import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # جایگزین کن با اسم پروژه
django.setup()

from prd_api.models import products
from django.contrib.auth.models import User

user = User.objects.get(id=5)

sample_data = [
    {
        "name": "Apple iPhone 15",
        "discription": "Latest iPhone with A17 chip.",
        "price": 999,
        "currency_type": "USD"
    },
    {
        "name": "Samsung Galaxy S24",
        "discription": "High-end Android smartphone.",
        "price": 850,
        "currency_type": "USD"
    },
    {
        "name": "Sony WH-1000XM5",
        "discription": "Noise cancelling wireless headphones.",
        "price": 400,
        "currency_type": "EUR"
    },
    {
        "name": "Canon EOS R7",
        "discription": "Mirrorless camera for professionals.",
        "price": 1500,
        "currency_type": "GBP"
    },
    {
        "name": "MacBook Pro 16",
        "discription": "Apple's flagship laptop for creatives.",
        "price": 2500,
        "currency_type": "USD"
    },
    {
        "name": "Asus ROG Laptop",
        "discription": "Gaming laptop with RTX graphics.",
        "price": 200000000,
        "currency_type": "IRR"
    },
    {
        "name": "Dyson Airwrap",
        "discription": "High-end hair styling tool.",
        "price": 600,
        "currency_type": "CAD"
    },
    {
        "name": "Nintendo Switch",
        "discription": "Portable gaming console.",
        "price": 299,
        "currency_type": "JPY"
    },
    {
        "name": "Logitech MX Master 3",
        "discription": "Ergonomic wireless mouse.",
        "price": 100,
        "currency_type": "CHF"
    },
    {
        "name": "Google Pixel 8",
        "discription": "Google's flagship phone.",
        "price": 799,
        "currency_type": "AUD"
    },
    {
        "name": "Xiaomi Smartwatch",
        "discription": "Affordable smartwatch with fitness tracking.",
        "price": 10000000,
        "currency_type": "IRR"
    },
    {
        "name": "PlayStation 5",
        "discription": "Next-gen gaming console by Sony.",
        "price": 500,
        "currency_type": "USD"
    },
    {
        "name": "Bose SoundLink",
        "discription": "Portable Bluetooth speaker.",
        "price": 150,
        "currency_type": "NZD"
    },
    {
        "name": "Dell XPS 13",
        "discription": "Premium ultrabook laptop.",
        "price": 1200,
        "currency_type": "EUR"
    },
    {
        "name": "Tesla Model 3 Toy",
        "discription": "Scale model of Tesla car.",
        "price": 90,
        "currency_type": "CNY"
    },
    {
        "name": "Samsung Monitor 32\"",
        "discription": "Curved QHD gaming monitor.",
        "price": 450,
        "currency_type": "INR"
    },
    {
        "name": "HP Laser Printer",
        "discription": "Fast and reliable printer.",
        "price": 200,
        "currency_type": "RUB"
    },
    {
        "name": "KitchenAid Mixer",
        "discription": "Multi-functional kitchen appliance.",
        "price": 350,
        "currency_type": "BRL"
    },
    {
        "name": "GoPro HERO12",
        "discription": "Action camera for adventure lovers.",
        "price": 450,
        "currency_type": "ZAR"
    },
    {
        "name": "Microsoft Surface Pro 9",
        "discription": "Versatile 2-in-1 Windows device.",
        "price": 999,
        "currency_type": "SGD"
    },
]

# ساخت نمونه‌ها
for item in sample_data:
    products.objects.create(user=user, **item)
