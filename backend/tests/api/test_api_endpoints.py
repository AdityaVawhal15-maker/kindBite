"""
KindBite API Tests
Tests API health, authentication, donation workflow, and ML prediction endpoints.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    resp = await async_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "kindbite-api"


@pytest.mark.asyncio
async def test_login_success_and_invalid(async_client: AsyncClient):
    # Valid login with seeded restaurant account
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "spicecraft@kindbite.in", "password": "KindBite@2026"},
    )
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

    # Invalid login
    bad_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "spicecraft@kindbite.in", "password": "WrongPassword123"},
    )
    assert bad_resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_analytics_with_login(async_client: AsyncClient):
    # Login as admin
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@kindbite.in", "password": "KindBite@2026"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.get("/api/v1/admin/analytics", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data
    assert "donations" in data
    assert data["users"]["total"] >= 10


@pytest.mark.asyncio
async def test_donations_list(async_client: AsyncClient):
    # Login as restaurant
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "spicecraft@kindbite.in", "password": "KindBite@2026"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = await async_client.get("/api/v1/donations", headers=headers)
    assert resp.status_code == 200
    donations = resp.json()
    assert isinstance(donations, list)
    assert len(donations) >= 1


@pytest.mark.asyncio
async def test_ml_prediction_inference(async_client: AsyncClient):
    login_resp = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "spicecraft@kindbite.in", "password": "KindBite@2026"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch food items to get valid ID
    items_resp = await async_client.get("/api/v1/restaurants/me/food-items", headers=headers)
    assert items_resp.status_code == 200
    items = items_resp.json()
    food_item_id = items[0]["id"] if items else None

    # Surplus prediction endpoint
    surplus_req = {
        "food_item_id": food_item_id,
        "prediction_date": "2026-11-15T12:00:00Z",
        "prepared_quantity_kg": 28.5,
    }
    resp = await async_client.post("/api/v1/predictions/surplus", json=surplus_req, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert "predicted_demand_kg" in data
    assert "predicted_surplus_kg" in data
    assert "waste_risk" in data
    assert data["predicted_surplus_kg"] >= 0
