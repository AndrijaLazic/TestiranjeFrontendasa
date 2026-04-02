from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest

sys.path.append(str(Path(__file__).resolve().parent))
import main  # noqa: E402

pytestmark = pytest.mark.anyio


@pytest.fixture
async def client() -> httpx.AsyncClient:
    main.reset_state()
    transport = httpx.ASGITransport(app=main.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def login(client: httpx.AsyncClient, username: str, password: str) -> dict[str, str]:
    response = await client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()


async def test_login_success_for_admin_and_user_and_invalid_credentials(client: httpx.AsyncClient) -> None:
    admin_login = await login(client, "admin", "admin123")
    assert admin_login["role"] == "admin"
    assert admin_login["token_type"] == "bearer"
    assert admin_login["access_token"]

    user_login = await login(client, "user", "user123")
    assert user_login["role"] == "user"
    assert user_login["token_type"] == "bearer"
    assert user_login["access_token"]

    invalid = await client.post("/auth/login", json={"username": "admin", "password": "wrong"})
    assert invalid.status_code == 401


async def test_all_protected_endpoints_reject_missing_token(client: httpx.AsyncClient) -> None:
    assert (await client.get("/products")).status_code == 401
    assert (await client.get("/categories")).status_code == 401
    assert (await client.get("/categories/1/subcategories")).status_code == 401

    create = await client.post(
        "/products",
        json={
            "name": "New Product",
            "price": 99.99,
            "category_id": 1,
            "sub_category_id": 101,
        },
    )
    assert create.status_code == 401


async def test_get_products_returns_seeded_sorted_results(client: httpx.AsyncClient) -> None:
    user_token = (await login(client, "user", "user123"))["access_token"]
    response = await client.get("/products", headers=auth_headers(user_token))
    assert response.status_code == 200

    products = response.json()
    assert len(products) == 1000

    sort_keys = [(item["category_id"], item["sub_category_id"], item["id"]) for item in products]
    assert sort_keys == sorted(sort_keys)


async def test_user_can_read_but_cannot_mutate_products(client: httpx.AsyncClient) -> None:
    user_token = (await login(client, "user", "user123"))["access_token"]
    headers = auth_headers(user_token)

    assert (await client.get("/products", headers=headers)).status_code == 200
    assert (await client.get("/categories", headers=headers)).status_code == 200

    create_response = await client.post(
        "/products",
        headers=headers,
        json={
            "name": "Blocked Product",
            "price": 150.0,
            "category_id": 1,
            "sub_category_id": 101,
        },
    )
    patch_response = await client.patch("/products/1", headers=headers, json={"name": "Blocked Update"})
    delete_response = await client.delete("/products/1", headers=headers)

    assert create_response.status_code == 403
    assert patch_response.status_code == 403
    assert delete_response.status_code == 403


async def test_admin_can_create_product_with_auto_incremented_id(client: httpx.AsyncClient) -> None:
    admin_token = (await login(client, "admin", "admin123"))["access_token"]
    headers = auth_headers(admin_token)

    before = (await client.get("/products", headers=headers)).json()
    max_id_before = max(item["id"] for item in before)

    create_response = await client.post(
        "/products",
        headers=headers,
        json={
            "name": "Admin Added Product",
            "price": 259.5,
            "category_id": 2,
            "sub_category_id": 201,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] == max_id_before + 1

    after = (await client.get("/products", headers=headers)).json()
    assert len(after) == 1001
    assert any(item["id"] == created["id"] for item in after)
    sort_keys = [(item["category_id"], item["sub_category_id"], item["id"]) for item in after]
    assert sort_keys == sorted(sort_keys)


async def test_admin_can_patch_product_and_invalid_taxonomy_is_rejected(client: httpx.AsyncClient) -> None:
    admin_token = (await login(client, "admin", "admin123"))["access_token"]
    headers = auth_headers(admin_token)

    patch_response = await client.patch(
        "/products/1",
        headers=headers,
        json={"name": "Updated Name", "price": 333.33},
    )
    assert patch_response.status_code == 200
    patched = patch_response.json()
    assert patched["id"] == 1
    assert patched["name"] == "Updated Name"
    assert patched["price"] == 333.33

    invalid_taxonomy = await client.patch(
        "/products/1",
        headers=headers,
        json={"category_id": 1, "sub_category_id": 201},
    )
    assert invalid_taxonomy.status_code == 422


async def test_admin_can_delete_product(client: httpx.AsyncClient) -> None:
    admin_token = (await login(client, "admin", "admin123"))["access_token"]
    headers = auth_headers(admin_token)

    delete_response = await client.delete("/products/1", headers=headers)
    assert delete_response.status_code == 204

    products = (await client.get("/products", headers=headers)).json()
    assert len(products) == 999
    assert not any(product["id"] == 1 for product in products)


async def test_get_categories_returns_five_seeded_categories(client: httpx.AsyncClient) -> None:
    token = (await login(client, "user", "user123"))["access_token"]
    response = await client.get("/categories", headers=auth_headers(token))
    assert response.status_code == 200

    categories = response.json()
    assert len(categories) == 5
    assert [item["id"] for item in categories] == [1, 2, 3, 4, 5]
    assert [item["name"] for item in categories] == [
        "CPU",
        "GPU",
        "Motherboard",
        "Memory",
        "Storage",
    ]


async def test_get_subcategories_by_category_and_unknown_category(client: httpx.AsyncClient) -> None:
    token = (await login(client, "user", "user123"))["access_token"]
    headers = auth_headers(token)

    response = await client.get("/categories/1/subcategories", headers=headers)
    assert response.status_code == 200
    subcategories = response.json()
    assert len(subcategories) == 4
    assert all(item["category_id"] == 1 for item in subcategories)

    missing = await client.get("/categories/999/subcategories", headers=headers)
    assert missing.status_code == 404
