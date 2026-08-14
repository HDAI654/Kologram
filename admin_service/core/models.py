"""
Unmanaged models mapped to AuthDB and MarketDB tables.

Tables are owned by Auth Service and Market Service.
This app only provides Django admin CRUD against those tables.
"""

from __future__ import annotations

from django.db import models

# ---------------------------------------------------------------------------
# AuthDB — users (Auth Service)
# ---------------------------------------------------------------------------


class AuthUser(models.Model):
    """Maps to Auth Service table `users`."""

    id = models.CharField(max_length=36, primary_key=True)
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    hashed_password = models.CharField(max_length=255)
    status = models.CharField(max_length=16, default="ACTIVE", db_index=True)

    class Meta:
        managed = False
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["email"]

    def __str__(self) -> str:
        return f"{self.email} ({self.status})"


# ---------------------------------------------------------------------------
# MarketDB — categories, listings, listing_images (Market Service)
# ---------------------------------------------------------------------------


class Category(models.Model):
    """Maps to Market Service table `categories`."""

    id = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=80, unique=True, db_index=True)
    parent_id = models.CharField(max_length=36, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "categories"
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Listing(models.Model):
    """Maps to Market Service table `listings`."""

    id = models.CharField(max_length=36, primary_key=True)
    seller_id = models.CharField(max_length=36, db_index=True)
    category_id = models.CharField(max_length=36, db_index=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    price_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, db_index=True)
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "listings"
        verbose_name = "Listing"
        verbose_name_plural = "Listings"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.title} [{self.status}]"


class ListingImage(models.Model):
    """Maps to Market Service table `listing_images`."""

    id = models.CharField(max_length=36, primary_key=True)
    listing_id = models.CharField(max_length=36, db_index=True)
    url = models.CharField(max_length=2048)
    sort_order = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "listing_images"
        verbose_name = "Listing image"
        verbose_name_plural = "Listing images"
        ordering = ["sort_order"]

    def __str__(self) -> str:
        return f"Image {self.id} (listing {self.listing_id})"
