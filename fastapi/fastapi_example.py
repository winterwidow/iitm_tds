from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid

app = FastAPI(
    title="TDS Tasks API",
    description="A simple task management API for the TDS course",
    version="1.0.0",
    docs_url="/docs",  # change URL if needed
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# --- Models ---
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    done: bool = False


class Task(TaskCreate):
    id: str


# --- In-memory store ---
tasks: dict[str, Task] = {}


# --- Routes ---
@app.get("/tasks", response_model=List[Task])
def list_tasks():
    return list(tasks.values())


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(payload: TaskCreate):
    task = Task(id=str(uuid.uuid4()), **payload.model_dump())
    tasks[task.id] = task
    return task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    return tasks[task_id]


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, payload: TaskCreate):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    tasks[task_id] = Task(id=task_id, **payload.model_dump())
    return tasks[task_id]


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(404, "Task not found")
    del tasks[task_id]
