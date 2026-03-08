import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient):
    await async_client.post("/api/v1/auth/register", json={
        "email": "tasktest@example.com",
        "password": "TestPass123!",
        "full_name": "Task Tester"
    })
    login = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "tasktest@example.com", "password": "TestPass123!"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_task_without_ratings_calls_gemini(async_client, auth_headers):
    """When impact/urgency/energy_required are omitted, Gemini should be called."""
    fake_entities = {
        "title": "Write report",
        "impact": 4,
        "urgency": 3,
        "energy_required": 2,
        "is_big_rock": False,
    }
    with patch(
        "app.routers.tasks.extract_task_entities",
        new=AsyncMock(return_value=fake_entities)
    ) as mock_gemini:
        resp = await async_client.post(
            "/api/v1/tasks",
            json={"title": "Write report", "description": "quarterly report"},
            headers=auth_headers,
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["impact"] == 4
    assert data["urgency"] == 3
    assert data["energy_required"] == 2
    mock_gemini.assert_called_once()


@pytest.mark.asyncio
async def test_create_task_with_explicit_ratings_skips_gemini(async_client, auth_headers):
    """When all ratings are provided, Gemini should NOT be called."""
    with patch(
        "app.routers.tasks.extract_task_entities",
        new=AsyncMock()
    ) as mock_gemini:
        resp = await async_client.post(
            "/api/v1/tasks",
            json={"title": "Manual task", "impact": 2, "urgency": 2, "energy_required": 1},
            headers=auth_headers,
        )
    assert resp.status_code == 201
    assert resp.json()["impact"] == 2
    mock_gemini.assert_not_called()
