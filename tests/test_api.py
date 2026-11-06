import uuid

import pytest
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError as RedisConnectionError

import server


class FakeRedis:
    """Test storage will be recreated for each tests."""

    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value
        return True

    def get(self, key):
        return self.data.get(key)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(server, "redis_client", FakeRedis())

    with TestClient(server.application) as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_query_two_tasks(client):
    task_ids = []

    for _ in range(2):
        response = client.post("/tasks")

        assert response.status_code == 201
        task = response.json()
        assert task["status"] == "pending"
        assert str(uuid.UUID(task["task_id"])) == task["task_id"]
        task_ids.append(task["task_id"])

    assert task_ids[0] != task_ids[1]

    for task_id in task_ids:
        response = client.get(
            "/task-status",
            params={"task_id": task_id},
        )

        assert response.status_code == 200
        assert response.json() == {
            "task_id": task_id,
            "status": "pending",
        }


def test_unknown_task(client):
    response = client.get(
        "/task-status",
        params={"task_id": "00000000-0000-0000-0000-000000000000"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@pytest.mark.parametrize("params", [{}, {"task_id": "abc"}])
def test_invalid_task_id(client, params):
    response = client.get("/task-status", params=params)

    assert response.status_code == 422


@pytest.mark.parametrize("operation", ["create", "query"])
def test_redis_unavailable(client, monkeypatch, operation):
    def fail(*args, **kwargs):
        raise RedisConnectionError("Simulated connection failure")

    monkeypatch.setattr(server.redis_client, "set", fail)
    monkeypatch.setattr(server.redis_client, "get", fail)

    if operation == "create":
        response = client.post("/tasks")
    else:
        response = client.get(
            "/task-status",
            params={"task_id": str(uuid.uuid4())},
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Task storage is unavailable",
    }