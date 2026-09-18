from django.contrib import admin
from core.models import AuthUser, Category, Listing, ListingImage

# ---------------------------------------------------------------------------
# AuthDB — users
# ---------------------------------------------------------------------------


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "status")
    list_filter = ("status",)
    search_fields = ("id", "email")
    ordering = ("email",)
    readonly_fields = ("hashed_password",)


# ---------------------------------------------------------------------------
# MarketDB — categories
# ---------------------------------------------------------------------------


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "parent_id", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("id", "name", "parent_id")
    ordering = ("name",)


# ---------------------------------------------------------------------------
# MarketDB — listings + images
# ---------------------------------------------------------------------------


class ListingImageInline(admin.TabularInline):
    """Edit a listing's images on the listing detail page."""

    model = ListingImage
    fk_name = "listing"
    extra = 1
    fields = ("id", "url", "sort_order")
    ordering = ("sort_order",)
    show_change_link = True


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
    inlines = [ListingImageInline]


@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "url", "sort_order")
    list_select_related = ("listing",)
    search_fields = ("id", "url", "listing__id", "listing__title")
    list_filter = ("sort_order",)
    ordering = ("listing_id", "sort_order")
    autocomplete_fields = ("listing",)
