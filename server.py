import uuid
import os

import redis
from fastapi import FastAPI, HTTPException
from redis.exceptions import RedisError

application = FastAPI(title="Task Service")

# FastAPI is currently running on the computer and connects to Redis in Docker through port 6380
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6380")),
    decode_responses=True,
    socket_connect_timeout=3,
    socket_timeout=3,
)


@application.get("/health")
def health():
    return {"status": "ok"}


@application.post("/tasks", status_code=201)
def create_task():
    task_id = str(uuid.uuid4())

    try:
        redis_client.set(f"task:{task_id}:status", "pending")
    except RedisError:
        raise HTTPException(
            status_code=503,
            detail="Task storage is unavailable",
        ) from None

    return {"task_id": task_id, "status": "pending"}


@application.get("/task-status")
def get_task_status(task_id: uuid.UUID):
    task_id_str = str(task_id)

    try:
        status = redis_client.get(f"task:{task_id_str}:status")
    except RedisError:
        raise HTTPException(
            status_code=503,
            detail="Task storage is unavailable",
        ) from None

    if status is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"task_id": task_id_str, "status": status}