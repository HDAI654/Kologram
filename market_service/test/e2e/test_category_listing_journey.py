"""E2E journey: full seller listing lifecycle over GraphQL."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from market_service.test.e2e.helpers import assert_error_code, assert_no_errors, gql

SELLER = "550e8400-e29b-41d4-a716-446655440000"
OTHER = "550e8400-e29b-41d4-a716-446655440099"

CREATE_CATEGORY = """
mutation CreateCategory($input: CreateCategoryInput!) {
  createCategory(input: $input) {
    categoryId
    name
    parentId
    isActive
  }
}
"""

CREATE_LISTING = """
mutation CreateListing($input: CreateListingInput!) {
  createListing(input: $input) {
    listingId
    status
  }
}
"""

UPDATE_LISTING = """
mutation UpdateListing($input: UpdateListingInput!) {
  updateListing(input: $input) {
    listingId
    status
  }
}
"""

PUBLISH_LISTING = """
mutation PublishListing($input: PublishListingInput!) {
  publishListing(input: $input) {
    listingId
    status
  }
}
"""

CHANGE_STATUS = """
mutation ChangeStatus($input: ChangeListingStatusInput!) {
  changeListingStatus(input: $input) {
    listingId
    status
  }
}
"""

DELETE_LISTING = """
mutation DeleteListing($input: DeleteListingInput!) {
  deleteListing(input: $input) {
    listingId
    deleted
  }
}
"""

GET_LISTING = """
query GetListing($id: String!) {
  listing(listingId: $id) {
    listingId
    title
    description
    status
    priceAmount
    currency
    quantity
    sellerId
    categoryId
    location
    images { id url sortOrder }
  }
}
"""

SEARCH = """
query Search($input: SearchListingsInput) {
  searchListings(input: $input) {
    items {
      listingId
      title
      status
      location
      sellerId
    }
    limit
    offset
  }
}
"""

SELLER_LISTINGS = """
query SellerListings($sellerId: String!) {
  sellerListings(sellerId: $sellerId) {
    listingId
    title
    status
    sellerId
  }
}
"""

CATEGORIES = """
query Categories($activeOnly: Boolean!) {
  categories(activeOnly: $activeOnly) {
    categoryId
    name
    isActive
  }
}
"""


@pytest.mark.asyncio
async def test_full_listing_lifecycle(client: AsyncClient) -> None:
    # 1. Create category
    body = await gql(
        client,
        CREATE_CATEGORY,
        {"input": {"name": "Electronics"}},
    )
    data = assert_no_errors(body)
    category_id = data["createCategory"]["categoryId"]
    assert data["createCategory"]["name"] == "Electronics"
    assert data["createCategory"]["isActive"] is True

    # 2. List categories
    body = await gql(client, CATEGORIES, {"activeOnly": True})
    data = assert_no_errors(body)
    assert any(c["categoryId"] == category_id for c in data["categories"])

    # 3. Create listing (DRAFT)
    body = await gql(
        client,
        CREATE_LISTING,
        {
            "input": {
                "sellerId": SELLER,
                "categoryId": category_id,
                "title": "MacBook Pro 14",
                "description": "M3 Pro, 18GB",
                "priceAmount": "1999.00",
                "currency": "USD",
                "quantity": 1,
                "location": "Berlin",
                "imageUrls": ["https://cdn.example.com/mbp.jpg"],
            }
        },
    )
    data = assert_no_errors(body)
    listing_id = data["createListing"]["listingId"]
    assert data["createListing"]["status"] == "DRAFT"

    # 4. Get draft listing
    body = await gql(client, GET_LISTING, {"id": listing_id})
    data = assert_no_errors(body)
    listing = data["listing"]
    assert listing["title"] == "MacBook Pro 14"
    assert listing["status"] == "DRAFT"
    assert listing["priceAmount"] == "1999.00"
    assert len(listing["images"]) == 1

    # 5. Update listing
    body = await gql(
        client,
        UPDATE_LISTING,
        {
            "input": {
                "listingId": listing_id,
                "sellerId": SELLER,
                "title": "MacBook Pro 14 M3",
                "priceAmount": "1899.50",
            }
        },
    )
    data = assert_no_errors(body)
    assert data["updateListing"]["listingId"] == listing_id

    body = await gql(client, GET_LISTING, {"id": listing_id})
    data = assert_no_errors(body)
    assert data["listing"]["title"] == "MacBook Pro 14 M3"
    assert data["listing"]["priceAmount"] == "1899.50"

    # 6. Publish
    body = await gql(
        client,
        PUBLISH_LISTING,
        {"input": {"listingId": listing_id, "sellerId": SELLER}},
    )
    data = assert_no_errors(body)
    assert data["publishListing"]["status"] == "ACTIVE"

    # 7. Search active
    body = await gql(
        client,
        SEARCH,
        {"input": {"query": "MacBook", "status": "ACTIVE"}},
    )
    data = assert_no_errors(body)
    ids = [i["listingId"] for i in data["searchListings"]["items"]]
    assert listing_id in ids

    # 8. Seller listings
    body = await gql(client, SELLER_LISTINGS, {"sellerId": SELLER})
    data = assert_no_errors(body)
    assert any(i["listingId"] == listing_id for i in data["sellerListings"])

    # 9. Mark sold
    body = await gql(
        client,
        CHANGE_STATUS,
        {
            "input": {
                "listingId": listing_id,
                "sellerId": SELLER,
                "newStatus": "SOLD",
            }
        },
    )
    data = assert_no_errors(body)
    assert data["changeListingStatus"]["status"] == "SOLD"


@pytest.mark.asyncio
async def test_delete_listing_journey(client: AsyncClient) -> None:
    body = await gql(client, CREATE_CATEGORY, {"input": {"name": "Books"}})
    category_id = assert_no_errors(body)["createCategory"]["categoryId"]

    body = await gql(
        client,
        CREATE_LISTING,
        {
            "input": {
                "sellerId": SELLER,
                "categoryId": category_id,
                "title": "Clean Code Book",
                "description": "Softcover",
                "priceAmount": "25.00",
                "quantity": 1,
                "location": "London",
            }
        },
    )
    listing_id = assert_no_errors(body)["createListing"]["listingId"]

    body = await gql(
        client,
        DELETE_LISTING,
        {"input": {"listingId": listing_id, "sellerId": SELLER}},
    )
    data = assert_no_errors(body)
    assert data["deleteListing"]["deleted"] is True

    body = await gql(client, GET_LISTING, {"id": listing_id})
    assert_error_code(body, "NOT_FOUND")


@pytest.mark.asyncio
async def test_forbidden_and_not_found(client: AsyncClient) -> None:
    body = await gql(client, CREATE_CATEGORY, {"input": {"name": "Gadgets"}})
    category_id = assert_no_errors(body)["createCategory"]["categoryId"]

    body = await gql(
        client,
        CREATE_LISTING,
        {
            "input": {
                "sellerId": SELLER,
                "categoryId": category_id,
                "title": "Wireless Mouse Item",
                "description": "",
                "priceAmount": "29.99",
                "quantity": 1,
                "location": "Berlin",
            }
        },
    )
    listing_id = assert_no_errors(body)["createListing"]["listingId"]

    # Wrong seller cannot update
    body = await gql(
        client,
        UPDATE_LISTING,
        {
            "input": {
                "listingId": listing_id,
                "sellerId": OTHER,
                "title": "Hacked Title Now",
            }
        },
    )
    assert_error_code(body, "FORBIDDEN")

    # Wrong seller cannot publish
    body = await gql(
        client,
        PUBLISH_LISTING,
        {"input": {"listingId": listing_id, "sellerId": OTHER}},
    )
    assert_error_code(body, "FORBIDDEN")

    # Unknown listing
    body = await gql(
        client,
        GET_LISTING,
        {"id": "550e8400-e29b-41d4-a716-446655440099"},
    )
    assert_error_code(body, "NOT_FOUND")


@pytest.mark.asyncio
async def test_publish_conflict_and_duplicate_category(client: AsyncClient) -> None:
    body = await gql(client, CREATE_CATEGORY, {"input": {"name": "UniqueCat"}})
    category_id = assert_no_errors(body)["createCategory"]["categoryId"]

    # Duplicate category name
    body = await gql(client, CREATE_CATEGORY, {"input": {"name": "UniqueCat"}})
    assert_error_code(body, "CONFLICT")

    body = await gql(
        client,
        CREATE_LISTING,
        {
            "input": {
                "sellerId": SELLER,
                "categoryId": category_id,
                "title": "Conflict Item Here",
                "description": "",
                "priceAmount": "10",
                "quantity": 1,
                "location": "Oslo",
            }
        },
    )
    listing_id = assert_no_errors(body)["createListing"]["listingId"]

    body = await gql(
        client,
        PUBLISH_LISTING,
        {"input": {"listingId": listing_id, "sellerId": SELLER}},
    )
    assert_no_errors(body)

    # Publish twice → conflict
    body = await gql(
        client,
        PUBLISH_LISTING,
        {"input": {"listingId": listing_id, "sellerId": SELLER}},
    )
    assert_error_code(body, "CONFLICT")
