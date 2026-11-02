"""
KindBite — Pytest configuration and shared fixtures
"""
from __future__ import annotations

import asyncio
import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models import User, UserRole


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def admin_token():
    return create_access_token("admin_test_user_id", extra={"role": UserRole.ADMIN.value, "email": "admin@kindbite.in"})


@pytest.fixture
def restaurant_token():
    return create_access_token("rest_test_user_id", extra={"role": UserRole.RESTAURANT.value, "email": "spicecraft@kindbite.in"})


@pytest.fixture
def ngo_token():
    return create_access_token("ngo_test_user_id", extra={"role": UserRole.NGO.value, "email": "annadaata@kindbite.in"})


@pytest.fixture
def volunteer_token():
    return create_access_token("vol_test_user_id", extra={"role": UserRole.VOLUNTEER.value, "email": "rahul.sharma@kindbite.in"})
