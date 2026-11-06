# FastAPI Task Service

A small task-status API built with FastAPI, Redis, and Docker Compose.

This project demonstrates task creation, UUID validation,
Redis storage, and containerized deployment.

## Features

- Create a task with a unique UUID.
- Query task status by UUID.
- Store task status in Redis.
- Return errors for unknown tasks and invalid task IDs.
- Start the API and Redis with Docker Compose.

## Requirements

- Docker Desktop, or Docker Engine with Docker Compose

## Quick Start

From the project directory, run:

```bash
docker compose up --build -d
```

Open the interactive API documentation:

http://127.0.0.1:8001/docs

Check that the API responds:

```bash
curl http://127.0.0.1:8001/health
```

Expected response:

```json
{"status": "ok"}
```

This endpoint checks API responsiveness only; it does not check Redis.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check API responsiveness |
| POST | `/tasks` | Create a task |
| GET | `/task-status?task_id=<UUID>` | Query a task |

### Create a Task

```bash
curl -X POST http://127.0.0.1:8001/tasks
```

The API returns HTTP 201 with a generated task ID:

```json
{
  "task_id": "733a4d30-08e5-4f7f-954e-df0c0d467511",
  "status": "pending"
}
```

### Query a Task

Replace `<TASK_ID>` with the ID returned when you created the task:

```bash
curl "http://127.0.0.1:8001/task-status?task_id=<TASK_ID>"
```

## Error Responses

- `404`: The task does not exist.
- `422`: The task ID is missing or is not a valid UUID.
- `503`: A Redis operation failed.

## View Logs

```bash
docker compose logs api
```

## Stop the Services

```bash
docker compose down
```

Redis data is stored in a named Docker volume and is retained
when the services are stopped with the command above.

## Current Scope

Tasks are created with the status `pending`.
There is currently no background worker to execute tasks
or update their status.

The project includes automated API tests.
It does not yet include authentication.
It is intended for local learning and demonstration.

## Run Tests

With Python 3.12 and a virtual environment activated, run:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The tests cover:

- API health response
- Creating and querying separate tasks
- Unknown task IDs
- Missing or invalid task IDs
- Redis failure handling

Tests use an in-memory Redis substitute and do not require
a running Redis server. They do not verify Docker networking
or Redis persistence.