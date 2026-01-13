import pytest
from fastapi.testclient import TestClient
from agent_ops.api import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_create_run():
    response = client.post(
        "/v1/runs",
        json={"prompt": "Test task", "workspace": "/tmp/test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "queued"


def test_get_run():
    # First create a run
    create_response = client.post(
        "/v1/runs",
        json={"prompt": "Test task"}
    )
    run_id = create_response.json()["id"]
    
    # Then retrieve it
    get_response = client.get(f"/v1/runs/{run_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == run_id


def test_get_nonexistent_run():
    response = client.get("/v1/runs/nonexistent-id")
    assert response.status_code == 404
