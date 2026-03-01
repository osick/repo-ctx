"""Progress endpoints for the repo-ctx API.

This module provides endpoints for tracking progress of long-running operations.
Includes Server-Sent Events (SSE) for real-time updates.
"""

import json
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from repo_ctx.services.progress import get_progress_registry, ProgressTracker


class CreateTaskRequest(BaseModel):
    """Request to create a progress task."""
    task_type: str = Field(..., description="Type of task (e.g., indexing, analysis)")
    total_steps: int = Field(..., description="Total number of steps")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UpdateTaskRequest(BaseModel):
    """Request to update a progress task."""
    current_step: Optional[int] = Field(None, description="Current step number")
    message: Optional[str] = Field(None, description="Progress message")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class CompleteTaskRequest(BaseModel):
    """Request to complete a progress task."""
    result: Optional[dict[str, Any]] = Field(None, description="Task result")
    message: str = Field(default="Completed", description="Completion message")


class FailTaskRequest(BaseModel):
    """Request to fail a progress task."""
    error: str = Field(..., description="Error description")
    message: str = Field(default="Failed", description="Failure message")


class ProgressResponse(BaseModel):
    """Progress task response."""
    task_id: str
    task_type: str
    total_steps: int
    current_step: int
    progress: float
    message: str
    status: str
    error: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class TaskListResponse(BaseModel):
    """Response with list of tasks."""
    tasks: list[ProgressResponse]
    total: int


def create_progress_router() -> APIRouter:
    """Create a progress router.

    Returns:
        Configured APIRouter.
    """
    router = APIRouter(tags=["progress"])

    @router.get("/progress/tasks", response_model=TaskListResponse)
    async def list_tasks() -> TaskListResponse:
        """List all progress tasks.

        Returns:
            TaskListResponse with all tasks.
        """
        registry = get_progress_registry()
        tasks = registry.get_all_tasks()

        return TaskListResponse(
            tasks=[
                ProgressResponse(**t.to_dict())
                for t in tasks
            ],
            total=len(tasks),
        )

    @router.get("/progress/tasks/{task_id}", response_model=ProgressResponse)
    async def get_task(task_id: str) -> ProgressResponse:
        """Get a progress task by ID.

        Args:
            task_id: Task identifier.

        Returns:
            ProgressResponse with task details.
        """
        registry = get_progress_registry()
        tracker = registry.get_task(task_id)

        if tracker is None:
            raise HTTPException(status_code=404, detail="Task not found")

        return ProgressResponse(**tracker.to_dict())

    @router.post("/progress/tasks", response_model=ProgressResponse)
    async def create_task(request: CreateTaskRequest) -> ProgressResponse:
        """Create a new progress task.

        Args:
            request: Task creation request.

        Returns:
            ProgressResponse with created task.
        """
        registry = get_progress_registry()
        tracker = registry.create_task(
            task_type=request.task_type,
            total_steps=request.total_steps,
            metadata=request.metadata,
        )

        return ProgressResponse(**tracker.to_dict())

    @router.patch("/progress/tasks/{task_id}", response_model=ProgressResponse)
    async def update_task(task_id: str, request: UpdateTaskRequest) -> ProgressResponse:
        """Update a progress task.

        Args:
            task_id: Task identifier.
            request: Update request.

        Returns:
            ProgressResponse with updated task.
        """
        registry = get_progress_registry()
        tracker = registry.get_task(task_id)

        if tracker is None:
            raise HTTPException(status_code=404, detail="Task not found")

        tracker.update(
            step=request.current_step,
            message=request.message,
            metadata=request.metadata,
        )

        return ProgressResponse(**tracker.to_dict())

    @router.post("/progress/tasks/{task_id}/complete", response_model=ProgressResponse)
    async def complete_task(task_id: str, request: CompleteTaskRequest) -> ProgressResponse:
        """Mark a progress task as completed.

        Args:
            task_id: Task identifier.
            request: Completion request.

        Returns:
            ProgressResponse with completed task.
        """
        registry = get_progress_registry()
        tracker = registry.get_task(task_id)

        if tracker is None:
            raise HTTPException(status_code=404, detail="Task not found")

        tracker.complete(result=request.result, message=request.message)

        return ProgressResponse(**tracker.to_dict())

    @router.post("/progress/tasks/{task_id}/fail", response_model=ProgressResponse)
    async def fail_task(task_id: str, request: FailTaskRequest) -> ProgressResponse:
        """Mark a progress task as failed.

        Args:
            task_id: Task identifier.
            request: Failure request.

        Returns:
            ProgressResponse with failed task.
        """
        registry = get_progress_registry()
        tracker = registry.get_task(task_id)

        if tracker is None:
            raise HTTPException(status_code=404, detail="Task not found")

        tracker.fail(error=request.error, message=request.message)

        return ProgressResponse(**tracker.to_dict())

    @router.delete("/progress/tasks/{task_id}")
    async def delete_task(task_id: str) -> dict[str, str]:
        """Delete a progress task.

        Args:
            task_id: Task identifier.

        Returns:
            Deletion confirmation.
        """
        registry = get_progress_registry()

        if not registry.remove_task(task_id):
            raise HTTPException(status_code=404, detail="Task not found")

        return {"status": "deleted", "task_id": task_id}

    @router.get("/progress/stream/{task_id}")
    async def stream_task_progress(task_id: str):
        """Stream progress updates using Server-Sent Events.

        Args:
            task_id: Task identifier.

        Returns:
            StreamingResponse with SSE events.
        """
        registry = get_progress_registry()
        tracker = registry.get_task(task_id)

        if tracker is None:
            raise HTTPException(status_code=404, detail="Task not found")

        async def event_generator():
            """Generate SSE events."""
            async for event in registry.stream_events(task_id, timeout=30.0):
                data = json.dumps(event)
                yield f"data: {data}\n\n"

                # Stop streaming if task is done
                if event.get("status") in ("completed", "failed"):
                    break

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.post("/progress/cleanup")
    async def cleanup_tasks(max_age_seconds: int = 3600) -> dict[str, int]:
        """Clean up completed and failed tasks.

        Args:
            max_age_seconds: Maximum age in seconds.

        Returns:
            Number of tasks removed.
        """
        registry = get_progress_registry()
        removed = registry.cleanup_completed(max_age_seconds=max_age_seconds)

        return {"removed": removed}

    return router
