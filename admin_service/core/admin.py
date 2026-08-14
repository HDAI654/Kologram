"""Register Auth + Market tables on the default Django admin site."""

from __future__ import annotations

from django.contrib import admin

from core.models import AuthUser, Category, Listing, ListingImage


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "status")
    list_filter = ("status",)
    search_fields = ("id", "email")
    ordering = ("email",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent_id", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("id", "name", "parent_id")
    ordering = ("name",)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "seller_id",
        "category_id",
        "price_amount",
        "currency",
        "quantity",
        "status",
        "location",
        "updated_at",
    )
    list_filter = ("status", "currency")
    search_fields = ("id", "title", "seller_id", "category_id", "location")
    ordering = ("-updated_at",)


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ("id", "listing_id", "url", "sort_order")
    search_fields = ("id", "listing_id", "url")
    ordering = ("listing_id", "sort_order")
