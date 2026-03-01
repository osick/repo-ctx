"""Task and progress reporting endpoints for the repo-ctx API.

This module provides endpoints for tracking long-running operations
using Server-Sent Events (SSE) for real-time progress updates.
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from repo_ctx.services.base import ServiceContext


class TaskInfo(BaseModel):
    """Task information."""
    id: str = Field(..., description="Unique task ID")
    type: str = Field(..., description="Task type (e.g., 'index', 'analyze')")
    status: str = Field(..., description="Task status (pending, running, completed, failed)")
    progress: float = Field(default=0.0, description="Progress percentage (0-100)")
    message: Optional[str] = Field(None, description="Current status message")
    created_at: str = Field(..., description="Task creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")
    result: Optional[dict[str, Any]] = Field(None, description="Task result (when completed)")
    error: Optional[str] = Field(None, description="Error message (when failed)")


class TaskListResponse(BaseModel):
    """Response with list of tasks."""
    count: int
    tasks: list[TaskInfo]


class TaskCreateRequest(BaseModel):
    """Request to create a new background task."""
    type: str = Field(..., description="Task type")
    params: dict[str, Any] = Field(default={}, description="Task parameters")


class TaskCreateResponse(BaseModel):
    """Response from creating a task."""
    id: str
    status: str
    message: str


# In-memory task storage (in production, use Redis or database)
_tasks: dict[str, dict[str, Any]] = {}


def create_tasks_router(context: ServiceContext) -> APIRouter:
    """Create a tasks router with the given service context.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured APIRouter.
    """
    router = APIRouter(tags=["tasks"])

    @router.get("/tasks", response_model=TaskListResponse)
    async def list_tasks(
        status: Optional[str] = Query(None, description="Filter by status"),
        limit: int = Query(50, ge=1, le=200, description="Maximum tasks to return"),
    ) -> TaskListResponse:
        """List all tasks.

        Args:
            status: Optional status filter.
            limit: Maximum tasks to return.

        Returns:
            TaskListResponse with list of tasks.
        """
        tasks = list(_tasks.values())

        if status:
            tasks = [t for t in tasks if t.get("status") == status]

        # Sort by created_at descending
        tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)

        return TaskListResponse(
            count=len(tasks),
            tasks=[
                TaskInfo(
                    id=t["id"],
                    type=t["type"],
                    status=t["status"],
                    progress=t.get("progress", 0.0),
                    message=t.get("message"),
                    created_at=t["created_at"],
                    updated_at=t.get("updated_at"),
                    result=t.get("result"),
                    error=t.get("error"),
                )
                for t in tasks[:limit]
            ],
        )

    @router.get("/tasks/{task_id}", response_model=TaskInfo)
    async def get_task(task_id: str) -> TaskInfo:
        """Get task details.

        Args:
            task_id: Task ID.

        Returns:
            TaskInfo with task details.

        Raises:
            HTTPException: If task not found.
        """
        task = _tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

        return TaskInfo(
            id=task["id"],
            type=task["type"],
            status=task["status"],
            progress=task.get("progress", 0.0),
            message=task.get("message"),
            created_at=task["created_at"],
            updated_at=task.get("updated_at"),
            result=task.get("result"),
            error=task.get("error"),
        )

    @router.get("/tasks/{task_id}/stream")
    async def stream_task_progress(task_id: str) -> StreamingResponse:
        """Stream task progress using Server-Sent Events.

        Args:
            task_id: Task ID.

        Returns:
            SSE stream with progress updates.
        """
        if task_id not in _tasks:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

        async def event_generator() -> AsyncGenerator[str, None]:
            """Generate SSE events for task progress."""
            last_progress = -1.0
            last_status = ""

            while True:
                task = _tasks.get(task_id)
                if not task:
                    yield f"event: error\ndata: Task not found\n\n"
                    break

                current_progress = task.get("progress", 0.0)
                current_status = task.get("status", "pending")
                current_message = task.get("message", "")

                # Send update if progress or status changed
                if current_progress != last_progress or current_status != last_status:
                    data = {
                        "id": task_id,
                        "status": current_status,
                        "progress": current_progress,
                        "message": current_message,
                    }

                    if current_status == "completed":
                        data["result"] = task.get("result")
                    elif current_status == "failed":
                        data["error"] = task.get("error")

                    import json
                    yield f"event: progress\ndata: {json.dumps(data)}\n\n"

                    last_progress = current_progress
                    last_status = current_status

                # Exit if task is finished
                if current_status in ("completed", "failed"):
                    yield f"event: done\ndata: {current_status}\n\n"
                    break

                await asyncio.sleep(0.5)  # Poll every 500ms

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.delete("/tasks/{task_id}")
    async def delete_task(task_id: str) -> dict[str, Any]:
        """Delete a task.

        Args:
            task_id: Task ID.

        Returns:
            Deletion result.
        """
        if task_id not in _tasks:
            raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")

        del _tasks[task_id]
        return {"deleted": True, "task_id": task_id}

    return router


# Helper functions for task management (used by other services)

def create_task(task_type: str, params: dict[str, Any] = None) -> str:
    """Create a new task.

    Args:
        task_type: Type of task.
        params: Task parameters.

    Returns:
        Task ID.
    """
    task_id = str(uuid.uuid4())
    _tasks[task_id] = {
        "id": task_id,
        "type": task_type,
        "status": "pending",
        "progress": 0.0,
        "message": "Task created",
        "params": params or {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None,
        "result": None,
        "error": None,
    }
    return task_id


def update_task(
    task_id: str,
    status: Optional[str] = None,
    progress: Optional[float] = None,
    message: Optional[str] = None,
    result: Optional[dict[str, Any]] = None,
    error: Optional[str] = None,
) -> bool:
    """Update task progress.

    Args:
        task_id: Task ID.
        status: New status.
        progress: New progress (0-100).
        message: Status message.
        result: Task result (for completed tasks).
        error: Error message (for failed tasks).

    Returns:
        True if updated, False if not found.
    """
    if task_id not in _tasks:
        return False

    task = _tasks[task_id]
    task["updated_at"] = datetime.utcnow().isoformat()

    if status is not None:
        task["status"] = status
    if progress is not None:
        task["progress"] = progress
    if message is not None:
        task["message"] = message
    if result is not None:
        task["result"] = result
    if error is not None:
        task["error"] = error

    return True


def get_task(task_id: str) -> Optional[dict[str, Any]]:
    """Get task by ID.

    Args:
        task_id: Task ID.

    Returns:
        Task dictionary or None.
    """
    return _tasks.get(task_id)
