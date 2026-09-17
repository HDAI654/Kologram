import uuid
import pytest
from src.fake_dev_data import (
    _DEV_ELECTRONICS_ID,
    _DEV_FURNITURE_ID,
    _DEV_LAPTOPS_ID,
    _DEV_SELLER_ID,
)

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_health_endpoint_reports_ok(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Read-side journeys
# ---------------------------------------------------------------------------


class TestCategoryQueries:
    def test_list_categories_returns_all_seeded(self, gql):
        result = gql("""
            query {
                categories { categoryId name parentId isActive }
            }
            """)

        assert "errors" not in result
        by_name = {c["name"]: c for c in result["data"]["categories"]}
        assert {"Electronics", "Laptops", "Furniture"} <= set(by_name)
        assert by_name["Laptops"]["parentId"] == _DEV_ELECTRONICS_ID
        assert by_name["Furniture"]["isActive"] is False

    def test_active_only_filters_inactive(self, gql):
        result = gql("""
            query {
                categories(activeOnly: true) { name isActive }
            }
            """)

        names = {c["name"] for c in result["data"]["categories"]}
        assert names == {"Electronics", "Laptops"}


class TestListingQueries:
    def test_fetch_full_listing_detail_includes_images(self, gql, seeded_camera_id):
        result = gql(
            """
            query GetListing($id: String!) {
                listing(listingId: $id) {
                    listingId
                    sellerId
                    title
                    status
                    images { url sortOrder }
                }
            }
            """,
            {"id": seeded_camera_id},
        )

        assert "errors" not in result
        listing = result["data"]["listing"]
        assert listing["title"] == "Vintage Film Camera"
        assert listing["status"] == "ACTIVE"
        assert listing["sellerId"] == _DEV_SELLER_ID
        assert [img["sortOrder"] for img in listing["images"]] == [0, 1]

    def test_search_defaults_to_active_status(self, gql):
        result = gql("""
            query {
                searchListings(input: {}) {
                    items { listingId status }
                }
            }
            """)

        statuses = {i["status"] for i in result["data"]["searchListings"]["items"]}
        assert statuses == {"ACTIVE"}

    def test_search_by_location_and_category(self, gql):
        result = gql("""
            query {
                searchListings(input: {categoryId: "%s", status: "ACTIVE"}) {
                    items { title categoryId }
                }
            }
            """ % _DEV_ELECTRONICS_ID)

        titles = {i["title"] for i in result["data"]["searchListings"]["items"]}
        assert titles == {"Vintage Film Camera"}

    def test_seller_listings_returns_only_owners(self, gql):
        result = gql(
            """
            query SellerListings($sellerId: String!) {
                sellerListings(sellerId: $sellerId) {
                    listingId sellerId
                }
            }
            """,
            {"sellerId": _DEV_SELLER_ID},
        )

        items = result["data"]["sellerListings"]
        assert len(items) == 2
        assert all(i["sellerId"] == _DEV_SELLER_ID for i in items)

    def test_seller_listings_empty_for_unknown_seller(self, gql):
        result = gql(
            """
            query SellerListings($sellerId: String!) {
                sellerListings(sellerId: $sellerId) { listingId }
            }
            """,
            {"sellerId": str(uuid.uuid4())},
        )

        assert result["data"]["sellerListings"] == []


# ---------------------------------------------------------------------------
# Write-side journeys
# ---------------------------------------------------------------------------


class TestCategoryMutations:
    def test_create_category_success(self, gql):
        result = gql(
            """
            mutation CreateCategory($input: CreateCategoryInput!) {
                createCategory(input: $input) {
                    categoryId name parentId isActive
                }
            }
            """,
            {"input": {"name": "Watches", "parentId": _DEV_ELECTRONICS_ID}},
        )

        assert "errors" not in result
        created = result["data"]["createCategory"]
        assert created["name"] == "Watches"
        assert created["parentId"] == _DEV_ELECTRONICS_ID
        assert created["isActive"] is True

        listed = gql("query { categories { name } }")
        assert "Watches" in {c["name"] for c in listed["data"]["categories"]}

    def test_create_category_duplicate_name_returns_conflict(self, gql):
        result = gql(
            """
            mutation CreateCategory($input: CreateCategoryInput!) {
                createCategory(input: $input) { categoryId }
            }
            """,
            {"input": {"name": "Electronics"}},
        )

        assert result["errors"][0]["extensions"]["code"] == "CONFLICT"

    def test_create_category_invalid_name_returns_validation_error(self, gql):
        result = gql(
            """
            mutation CreateCategory($input: CreateCategoryInput!) {
                createCategory(input: $input) { categoryId }
            }
            """,
            {"input": {"name": "x"}},
        )

        assert result["errors"][0]["extensions"]["code"] == "VALIDATION_ERROR"

    def test_create_category_missing_parent_returns_not_found(self, gql):
        result = gql(
            """
            mutation CreateCategory($input: CreateCategoryInput!) {
                createCategory(input: $input) { categoryId }
            }
            """,
            {"input": {"name": "Watches", "parentId": str(uuid.uuid4())}},
        )

        assert result["errors"][0]["extensions"]["code"] == "NOT_FOUND"


class TestListingMutations:
    def test_create_listing_in_draft_with_images(self, gql):
        result = gql(
            """
            mutation CreateListing($input: CreateListingInput!) {
                createListing(input: $input) { listingId status }
            }
            """,
            {
                "input": {
                    "sellerId": _DEV_SELLER_ID,
                    "categoryId": _DEV_ELECTRONICS_ID,
                    "title": "Mechanical Keyboard",
                    "description": "Tactile switches, hot-swappable.",
                    "priceAmount": "129.00",
                    "currency": "USD",
                    "quantity": 2,
                    "location": "Berlin",
                    "imageUrls": [
                        "https://example.com/kb-front.jpg",
                        "https://example.com/kb-back.jpg",
                    ],
                }
            },
        )

        assert "errors" not in result
        created = result["data"]["createListing"]
        assert created["status"] == "DRAFT"

        detail = gql(
            """
            query GetListing($id: String!) {
                listing(listingId: $id) {
                    title
                    status
                    images { url sortOrder }
                }
            }
            """,
            {"id": created["listingId"]},
        )
        images = detail["data"]["listing"]["images"]
        assert [i["sortOrder"] for i in images] == [0, 1]
        assert images[0]["url"] == "https://example.com/kb-front.jpg"

    def test_create_listing_with_inactive_category_returns_conflict(self, gql):
        result = gql(
            """
            mutation CreateListing($input: CreateListingInput!) {
                createListing(input: $input) { listingId }
            }
            """,
            {
                "input": {
                    "sellerId": _DEV_SELLER_ID,
                    "categoryId": _DEV_FURNITURE_ID,
                    "title": "Oak Dining Table",
                    "description": "Solid oak.",
                    "priceAmount": "899.00",
                    "quantity": 1,
                    "location": "Amsterdam",
                }
            },
        )

        assert result["errors"][0]["extensions"]["code"] == "CONFLICT"

    def test_create_listing_with_unknown_category_returns_not_found(self, gql):
        result = gql(
            """
            mutation CreateListing($input: CreateListingInput!) {
                createListing(input: $input) { listingId }
            }
            """,
            {
                "input": {
                    "sellerId": _DEV_SELLER_ID,
                    "categoryId": str(uuid.uuid4()),
                    "title": "Random Item",
                    "description": "No category.",
                    "priceAmount": "10.00",
                    "quantity": 1,
                    "location": "Nowhere",
                }
            },
        )

        assert result["errors"][0]["extensions"]["code"] == "NOT_FOUND"

    def test_update_listing_wrong_seller_returns_forbidden(self, gql, seeded_camera_id):
        result = gql(
            """
            mutation UpdateListing($input: UpdateListingInput!) {
                updateListing(input: $input) { listingId status }
            }
            """,
            {
                "input": {
                    "listingId": seeded_camera_id,
                    "sellerId": str(uuid.uuid4()),
                    "title": "Hijacked",
                }
            },
        )

        assert result["errors"][0]["extensions"]["code"] == "FORBIDDEN"

    def test_publish_listing_from_non_draft_returns_conflict(
        self, gql, seeded_camera_id
    ):
        # Seeded camera is ACTIVE → DRAFT→ACTIVE only, so publish again is invalid.
        result = gql(
            """
            mutation PublishListing($input: PublishListingInput!) {
                publishListing(input: $input) { listingId status }
            }
            """,
            {"input": {"listingId": seeded_camera_id, "sellerId": _DEV_SELLER_ID}},
        )

        assert result["errors"][0]["extensions"]["code"] == "CONFLICT"

    def test_delete_listing_wrong_seller_returns_forbidden(self, gql, seeded_camera_id):
        result = gql(
            """
            mutation DeleteListing($input: DeleteListingInput!) {
                deleteListing(input: $input) { listingId deleted }
            }
            """,
            {"input": {"listingId": seeded_camera_id, "sellerId": str(uuid.uuid4())}},
        )

        assert result["errors"][0]["extensions"]["code"] == "FORBIDDEN"


# ---------------------------------------------------------------------------
# Error-code matrix
# ---------------------------------------------------------------------------


class TestErrorCodes:
    def test_unknown_listing_returns_not_found(self, gql):
        result = gql(
            """
            query GetListing($id: String!) { listing(listingId: $id) { listingId } }
            """,
            {"id": str(uuid.uuid4())},
        )

        assert result["errors"][0]["extensions"]["code"] == "NOT_FOUND"

    def test_invalid_listing_id_returns_validation_error(self, gql):
        result = gql(
            """
            query GetListing($id: String!) { listing(listingId: $id) { listingId } }
            """,
            {"id": "not-a-uuid"},
        )

        assert result["errors"][0]["extensions"]["code"] == "VALIDATION_ERROR"

    def test_unknown_internal_error_is_not_leaked(self, gql, monkeypatch):
        """An unexpected exception must surface a generic message, not details."""
        from src.application.get_listing import GetListingHandler

        async def _boom(self, query):  # pragma: no cover - exercised below
            raise RuntimeError("connection string: postgres://secret")

        monkeypatch.setattr(GetListingHandler, "handle", _boom)

        result = gql(
            """
            query GetListing($id: String!) { listing(listingId: $id) { listingId } }
            """,
            {"id": str(uuid.uuid4())},
        )

        assert result["errors"][0]["extensions"]["code"] == "INTERNAL_ERROR"
        assert result["errors"][0]["message"] == "An internal error occurred"
        assert "postgres://secret" not in result["errors"][0]["message"]


# ---------------------------------------------------------------------------
# Full lifecycle (composite journey)
# ---------------------------------------------------------------------------


class TestFullListingLifecycle:
    def test_create_publish_update_sell_delete(self, gql):
        # 1. Create a fresh category to attach the listing to.
        created_category = gql(
            """
            mutation CreateCategory($input: CreateCategoryInput!) {
                createCategory(input: $input) { categoryId }
            }
            """,
            {"input": {"name": "Watches"}},
        )
        category_id = created_category["data"]["createCategory"]["categoryId"]

        # 2. Create the listing in DRAFT.
        created_listing = gql(
            """
            mutation CreateListing($input: CreateListingInput!) {
                createListing(input: $input) { listingId status }
            }
            """,
            {
                "input": {
                    "sellerId": _DEV_SELLER_ID,
                    "categoryId": category_id,
                    "title": "Omega Seamaster",
                    "description": "Vintage dive watch.",
                    "priceAmount": "2500.00",
                    "currency": "USD",
                    "quantity": 1,
                    "location": "Zurich",
                    "imageUrls": ["https://example.com/omega.jpg"],
                }
            },
        )
        assert "errors" not in created_listing
        listing_id = created_listing["data"]["createListing"]["listingId"]
        assert created_listing["data"]["createListing"]["status"] == "DRAFT"

        # 3. Publish → ACTIVE.
        published = gql(
            """
            mutation PublishListing($input: PublishListingInput!) {
                publishListing(input: $input) { listingId status }
            }
            """,
            {"input": {"listingId": listing_id, "sellerId": _DEV_SELLER_ID}},
        )
        assert published["data"]["publishListing"]["status"] == "ACTIVE"

        # 4. Update mutable fields while editable.
        updated = gql(
            """
            mutation UpdateListing($input: UpdateListingInput!) {
                updateListing(input: $input) { listingId status }
            }
            """,
            {
                "input": {
                    "listingId": listing_id,
                    "sellerId": _DEV_SELLER_ID,
                    "priceAmount": "2300.00",
                    "quantity": 1,
                    "location": "Basel",
                }
            },
        )
        assert "errors" not in updated

        # 5. Transition → SOLD.
        sold = gql(
            """
            mutation ChangeListingStatus($input: ChangeListingStatusInput!) {
                changeListingStatus(input: $input) { listingId status }
            }
            """,
            {
                "input": {
                    "listingId": listing_id,
                    "sellerId": _DEV_SELLER_ID,
                    "newStatus": "SOLD",
                }
            },
        )
        assert sold["data"]["changeListingStatus"]["status"] == "SOLD"

        # 6. Editing a SOLD listing is now a conflict.
        blocked = gql(
            """
            mutation UpdateListing($input: UpdateListingInput!) {
                updateListing(input: $input) { listingId status }
            }
            """,
            {
                "input": {
                    "listingId": listing_id,
                    "sellerId": _DEV_SELLER_ID,
                    "title": "Should not change",
                }
            },
        )
        assert blocked["errors"][0]["extensions"]["code"] == "CONFLICT"

        # 7. Delete.
        deleted = gql(
            """
            mutation DeleteListing($input: DeleteListingInput!) {
                deleteListing(input: $input) { listingId deleted }
            }
            """,
            {"input": {"listingId": listing_id, "sellerId": _DEV_SELLER_ID}},
        )
        assert deleted["data"]["deleteListing"]["deleted"] is True

        # 8. Final observable state: the listing is gone.
        after = gql(
            """
            query GetListing($id: String!) { listing(listingId: $id) { listingId } }
            """,
            {"id": listing_id},
        )
        assert after["errors"][0]["extensions"]["code"] == "NOT_FOUND"
